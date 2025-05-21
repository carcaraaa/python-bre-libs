from business_rule_engine import RuleParser

# suppose these are the percentage usage of some storage endpoints
endpoint_info = [
    {"endpoint_name": "endpoint-0", "usage_percentage": 50, "email": "user1@email.com"},
    {"endpoint_name": "endpoint-1","usage_percentage": 10,"email": "user2@email.com"},
    {"endpoint_name": "endpoint-2","usage_percentage": 80,"email": "user3@email.com"},
    {"endpoint_name": "endpoint-3","usage_percentage": 5,"email": "user4@email.com"},
]


# if a business rule is activated then this function will be executed
def notify_user(user, email):
    print(f"Please notify user {user} ({email}) for underused storage!")


# suppose this is the business rule active
rules = """
rule "notify underused space"
when
    usage_percentage < 20
then
    notify_user(endpoint_name, email)
end
"""

parser = RuleParser()
parser.register_function(notify_user)
parser.parsestr(rules)

for data in endpoint_info:
    parser.execute(data)
