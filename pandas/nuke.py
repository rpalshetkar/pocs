from faker import Faker

fake = Faker()


class Email:

    def __init__(self, to, cc, title, department, subject):
        self.to = to
        self.cc = cc
        self.title = title
        self.department = department
        self.subject = subject

    def __repr__(self):
        return f"Email(to={self.to}, cc={self.cc}, title={self.title}, department={self.department}, subject={self.subject})"


def generate_emails(num_emails):
    emails = []
    for _ in range(num_emails):
        to = fake.email()
        cc = [
            fake.email() for _ in range(fake.random_int(0, 5))
        ]  # Random number of cc recipients
        title = fake.sentence(
            nb_words=5, variable_nb_words=True, ext_word_list=None
        )
        department = fake.job()
        subject = fake.catch_phrase()
        emails.append(Email(to, cc, title, department, subject))
    return emails


# Generate 5 random email objects
emails = generate_emails(5)

# Print the generated email objects
for email in emails:
    print(email)
