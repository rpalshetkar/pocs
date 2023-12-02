import csv
import datetime
import hashlib
import multiprocessing
import re
import win32com.client
import pythoncom  # Added this line

class Subject:
    def actions(self, **msg):
        pass

class CacheListener(Subject):
    def __init__(self, cache, subscribers):
        self.cache = cache
        self.subscribers = subscribers

    def actions(self, **msg):
        self.update_realtime_cache(msg)
        self.notify_subscribers(msg)

    def update_realtime_cache(self, msg):
        message_id = self.generate_message_id(msg)
        self.cache[message_id] = msg

    def generate_message_id(self, msg):
        hash_string = f'{msg["From"]}_{msg["To"]}_{msg["Subject"]}'
        return hashlib.md5(hash_string.encode()).hexdigest()

    def notify_subscribers(self, msg):
        for subscriber in self.subscribers:
            subscriber.update(msg)

class OutlookMessageListener:
    def __init__(self, cache_listener):
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        self.inbox = self.namespace.GetDefaultFolder(6)  # 6 represents the Inbox folder
        self.items = self.inbox.Items
        self.cache_listener = cache_listener

    def start_listening(self):
        self.items.ItemAdd += self.on_message_received
        while True:
            pythoncom.PumpWaitingMessages()  # pythoncom is now defined

    def on_message_received(self, item):
        msg = self.extract_msg(item)
        self.cache_listener.actions(**msg)

    def is_in_dg(self, email, dgs):
        user = self.namespace.CreateRecipient(email)
        exchange_user = user.GetExchangeUser()
        if exchange_user is not None:
            member_of = exchange_user.GetMemberOfList()
            for group in member_of:
                if group.lower() in dgs:
                    return True

    def get_dg_members(self, dgs):
        dg_members = []
        for dg_name in dgs:
            dg = self.namespace.CreateRecipient(dg_name)
            exchange_dg = dg.GetExchangeDistributionList()
            if exchange_dg is not None:
                members = exchange_dg.GetMembers()
                dg_members.extend(members)
        return list(set(dg_members))

    cleanse_addr = lambda addr: ";".join(address.strip().replace("#", "") for address in addr.split(";"))
    cleanse = lambda x: re.sub(r"^[:a-Z]", "", x)
    cleanse_alpha = lambda x: re.sub(r"^[a-Z]", "", x)

    def extract_msg(self, item):
        msg = {
            "time": item.ReceivedTime,
            "from": item.SenderName,
            "to": self.cleanse_addr(item.To), 
            "cc": self.cleanse_addr(item.CC),
        }
        subject = item.Subject
        if re.match(r"^(RE|FW):", subject):
            subject = re.sub(r"^(RE|FW):", "", subject).strip()
            msg["is_reply"] = True
        msg["subject"] = self.cleanse(subject)

        sender = self.namespace.CreateRecipient(item.SenderName)
        address_type = sender.AddressEntry.AddressEntryUserType
        if address_type == 0:  # olExchangeUserAddressEntry
            exchange_user = sender.GetExchangeUser()
            if exchange_user is not None:
                msg["title"] = exchange_user.JobTitle
                msg["dept"] = exchange_user.Department
        elif address_type == 10:  # olSmtpAddressEntry
            msg["smtp"] = sender.Address
        return msg

    def check_unanswered_messages(self, minutes, folder):
        important_messages = folder.Items.Restrict("[Importance]=2")  # Filter for important messages
        current_time = datetime.datetime.now()
        for message in important_messages:
            conversation = message.GetConversation()
            if conversation is not None:
                root_items = conversation.GetRootItems()
                for item in root_items:
                    if item.ReceivedTime <= current_time - datetime.timedelta(minutes=minutes):
                        if not item.Categories:  # Check if the message has not been responded to
                            print(f'Important message "{item.Subject}" has not been responded to for {minutes} minutes.')

    def traverse_folders(self, minutes, folder):
        self.check_unanswered_messages(minutes, folder)
        if folder.Folders.Count > 0:
            for subfolder in folder.Folder:
                self.traverse_folders(minutes, subfolder)


class CsvWriter:
    def __init__(self, filename, header_fields):
        self.filename = filename
        self.header_fields = header_fields

    def update(self, msg):
        day_of_week = datetime.datetime.now().strftime('%A')
        filename = f"{self.filename}_{day_of_week}.csv"
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(self.header_fields)
            writer.writerow(msg.values())

    def write_header(self):
        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.header_fields)


class RulesEngine:
    def __init__(self, rules):
        self.rules = rules

    def update(self, msg):
        self.rules.apply_rules(msg)


class Rule:
    def __init__(self, fields, regex, action, condition):
        self.fields = fields
        self.regex = regex
        self.action = action
        self.condition = condition

    def match(self, msg):
        for field in self.fields:
            value = msg.get(field)
            if value and not re.search(self.regex, value, re.IGNORECASE):
                return False
        return self.condition(msg)


class Rules:
    def __init__(self, rules_file):
        self.rules_file = rules_file
        self.rules = self.load_rules()

    def load_rules(self):
        rules = []
        with open(self.rules_file, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                fields = row[:-3]
                regex = row[-3]
                action = row[-2]
                condition = eval(row[-1])  # Evaluate the condition lambda from the string
                rule = Rule(fields, regex, action, condition)
                rules.append(rule)
        return rules

    def append_rule(self, fields, regex, action, condition):
        with open(self.rules_file, "a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(self.header_fields)
            writer.writerow(fields + [regex, action, condition])
        self.rules.append(Rule(fields, regex, action, condition))

    def apply_rules(self, msg):
        for rule in self.rules:
            if rule.match(msg):
                self.perform_action(rule.action, msg)

    def perform_action(self, action, msg):
        # Perform the desired action based on the rule
        # For example, you can print a message or modify the msg
        print(f"Rule matched: {action}")
        print(f"msg: {msg}")
        print("---")



if __name__ == "__main__":
    cache = {}
    subscribers = []

    csv_filename = "index"
    header_fields = ["Time", "From", "To", "Subject"]
    csv_writer = CsvWriter(csv_filename, header_fields)
    subscribers.append(csv_writer)

    rules_file = "rules.csv"
    rules = Rules(rules_file)
    rule_engine = RulesEngine(rules)
    subscribers.append(rule_engine)

    cache_listener = CacheListener(cache, subscribers)
    outlook_listener = OutlookMessageListener(cache_listener)

    pool = multiprocessing.Pool()
    pool.apply_async(outlook_listener.start_listening)