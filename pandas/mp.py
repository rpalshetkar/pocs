import glob
import os
import random
import re
from datetime import datetime
from multiprocessing import Lock, Pool

from faker import Faker

import pandas as pd

file_lock = Lock()
Faker.seed(1000)
fake = Faker()

random.seed(1000)


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


class Email:

    def __init__(self):
        email = self.generate_fake_email()
        self.sender = email["Sender"]
        self.to = email["To"]
        self.cc = email["CC"]
        self.subject = email["Subject"]
        self.ts = email["Ts"]
        self.title = email["Title"]
        self.department = email["Department"]
        self.rule = ""
        self.args = ""
        self.id = self.ts

    def __repr__(self):
        return f'{self.sender}|{self.title}|{self.department}|{",".join(self.to)}|{",".join(self.cc)}|{self.subject}|{self.ts}||'

    def generate_fake_email(self):
        title = random.choice(
            ["Managing Director", "Director", "Vice President", "Officer"]
        )
        department = random.choice(
            ["Technology", "Operations", "Finance", "HR", "Trading"]
        )
        si = random.randint(1, 50)
        toi = random.randint(1, 250)
        cci = random.randint(1, 500)
        sender = fake.email(domain="system.com" if si % 5 == 0 else "bofa.com")
        if title == "Managing Director":
            sender = f"MD{si}@bofa.com"
        to = [
            fake.email(domain="system.com" if toi % 7 == 0 else "bofa.com")
            for _ in range(random.randint(1, 3))
        ]
        cc = [
            fake.email(domain="system.com" if cci % 3 == 0 else "bofa.com")
            for _ in range(random.randint(0, 3))
        ]
        subject = fake.sentence()
        body = fake.paragraph()
        if si % 8 == 0:
            to = ["me@bofa.com"]
        if si % 5 == 0:
            to.append("me@bofa.com")
        if si % 6 == 0:
            cc.append("me@bofa.com")
        if toi % 5 == 0:
            to.append("slt@bofa.com")
        if cci % 7 == 0:
            cc.append("vipdg@bofa.com")
        if cci % 6 == 0:
            subject += "Spam Subject"
        if si % 25 == 0:
            sender = "Spammer@bofa.com"
        return {
            "Title": title,
            "Department": department,
            "Sender": sender,
            "To": list(set(to)),
            "CC": list(set(cc)),
            "Ts": ts(),
            "Subject": subject,
            "Body": body,
        }


def generate_email():
    count = 0
    while True:
        email = Email()
        print(f"Generated email {email}")
        yield email
        count += 1
        if count == 5000:
            break


def get_minute_file_path():
    prefix = datetime.now().strftime("%H.%w")
    file_name = f"emails.{prefix}.csv"
    return file_name


def save_email_to_file(email):
    fp = get_minute_file_path()
    if not os.path.exists(fp):
        with file_lock:
            with open(fp, "w") as file:
                file.write("Sender|Title|Department|To|CC|Subject|Ts|Rule|Args\n")

    with file_lock:
        print(email)
        try:
            with open(fp, "a") as file:
                file.write(f"{email}\n")
        except Exception as e:
            print(f"Exception {e}")


def label_email(email):
    print(f"Labeling email {email}")


def setup():
    pool = Pool()
    email_generator = generate_email()
    for email in email_generator:
        pool.apply_async(save_email_to_file, args=(email,))
        pool.apply_async(label_email, args=(email,))
    pool.close()
    pool.join()


def read_csvs(fpattern):
    csvs = glob.glob(fpattern)
    dfs = []
    for csv_file in csvs:
        df = pd.read_csv(csv_file, sep="|", header=0)
        df.columns = [i.lower() for i in df.columns]
        dfs.append(df)
    cdf = pd.concat(dfs, ignore_index=True)
    df = pd.DataFrame(cdf)
    return df


def has_matching_element(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    return bool(set1.intersection(set2))


def apply_regex(row, pattern):
    for col in row.index:
        if pd.notna(row[col]):
            if bool(re.search(pattern, str(row[col]))):
                return True
    return False


def group_count(df, columns, greater_than):
    grouped_counts = df.groupby(columns).size().reset_index(name="count")
    filtered = grouped_counts[grouped_counts["count"] > greater_than]
    filtered = filtered.sort_values(by="count", ascending=False)
    return filtered


def populate_keys_values(row):
    cols = ["sender", "to", "cc", "title", "department", "dg", "date"]
    keys = [col for col in cols if pd.notnull(row[col])]
    values = [str(row[col]) for col in cols if pd.notnull(row[col])]
    return pd.Series({"fields": "/".join(keys), "values": "/".join(values)})


def labels(row, rules):
    print("------------------")
    for rule in rules:
        if "dg" in rule["fields"] or "date" in rule["fields"]:
            continue
        print(rule)
        col = f"is_{rule['rule']}".lower()
        for to_match in rule["regex"]:
            in_row = [row.get(i) for i in rule["fields"]]
            print(to_match, in_row)
            matched = all([re.match(v, to_match[i]) for i, v in enumerate(in_row)])
            if matched:
                row[col] = True
    return row


def parse_rules(rules_file):
    rdf = read_csvs(rules_file)
    rdf[["fields", "values"]] = rdf.apply(populate_keys_values, axis=1)
    print(rdf[["rule", "queue", "priority", "action", "args", "fields", "values"]])
    uniques = (
        rdf.groupby(["queue", "priority", "action", "args", "fields", "rule"])["values"]
        .unique()
        .reset_index()
    )
    rules = uniques.to_dict(orient="records")
    for rule in rules:
        fields = rule.get("fields", "")
        values = list(rule.get("values", []))
        fields = fields.split("/")
        rule["fields"] = fields
        if len(fields) == 1:
            rule["regex"] = [re.compile("|".join(values))]
            rule["regex"] = [values or ""]
        else:
            rule["field_wise"] = True
            rule["regex"] = [i.split("/") for i in values]
    return rules


def tag_messages():
    mdf = read_csvs("emails.*.csv").fillna("").head(100)
    rules = parse_rules("rules.csv")
    mdf = mdf.apply(lambda x: labels(x, rules), axis=1)
    print(mdf[["sender", "to", "is_md", "is_meto", "is_mecc"]])


"""
    df = read_csvs("emails.*.csv").fillna("")
    vips = ["vipdg@bofa.com", "slt@bofa.com", "rslt2@bofa.com"]
    df["is_vip"] = df["sender"].str.contains("MD")
    df["is_to_me"] = df["to"].str.contains("me@bofa.com")
    df["is_cc_me"] = df["cc"].str.contains("me@bofa.com")
    df["is_system"] = df["sender"].str.contains("system.com")
    df["is_spam"] = df["sender"].str.contains("Spammer") | df["subject"].str.contains(
        "spam"
    )
    df["is_only_to"] = ~df["to"].str.contains(",") & df["is_to_me"]
    df["is_only_cc"] = ~df["cc"].str.contains(",") & df["is_cc_me"]
    df["is_vip"] = df["sender"].apply(
        lambda x: has_matching_element(x.split(","), ["Managing Director"])
    )
    df["is_vip_dg"] = df.apply(
        lambda x: has_matching_element((x["to"] + x["cc"]).split(","), vips), axis=1
    )
    flags = [i for i in df.columns if i.startswith("is_")]
    show = ["sender", "to", "cc"]
    for flag in flags:
        print(f"-----------------\nFlag {flag}\n-------------------\n")
        mask = df[flag]
        print(df[mask].head(10)[show])

    for field in ["sender", "title", "department"]:
        print(f"-----------------\nField {field}\n-------------------\n")
        print(group_count(df, [field], 10))
        uniques = df[field].unique()

        rpattern = "|".join(map(re.escape, uniques))
    """

if __name__ == "__main__":
    pd.set_option("display.width", 500)
    pd.set_option("display.max_colwidth", 40)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", 20)
    # setup()
    tag_messages()
"""
def create_folder(path, parent_folder):
    folders = path.split("/")
    for folder_name in folders:
        try:
            folder = parent_folder.Folders(folder_name)
        except Exception as e:
            folder = parent_folder.Folders.Add(folder_name)
        parent_folder = folder
    return folder

outlook = win32com.client.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
root= namespace.GetDefaultFolder(6)
folder_path = "Top Folder/Sub Folder1/Sub Folder2"
folder = create_folder(folder_path, root)


def get_dg_members(dg_name):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    dg = outlook.CreateRecipient(dg_name).AddressEntry.GetExchangeUser()
    members = dg.GetMemberOfList()
    return [member.PrimarySmtpAddress for member in members]

def is_dg_member(user, dg_members):
    return user in dg_members

if is_user_member_of_distribution_group(user_email, dg_name):
    print(f"{user_email} is a member of {dg_name}")
else:
    print(f"{user_email} is not a member of {dg_name}")
"""
