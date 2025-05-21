from datetime import datetime
from dataclasses import dataclass, asdict

from durable.lang import *


@dataclass
class DataEndpoint:
  endpoint_identifier: str
  space_quota: int
  space_used: int
  associated_email: str
  last_access: str # error on post because datetime is no serializable, change to str
  current_usage_percentage: float = .0
  days_since_last_access: int = 0

  def __post_init__(self) -> None:
    self.current_usage_percentage = (self.space_used * 100) / self.space_quota

    last_access_date = datetime.strptime(self.last_access, '%Y-%m-%d')
    self.days_since_last_access = (datetime.now() - last_access_date).days


def send_email(destination, message) -> None:
  print(f"Sending e-mail to '{destination}' regarding '{message}'")


with ruleset('data_endpoint'):
  @when_all(m.current_usage_percentage <= 20)
  def under_usage_resource(c):
    send_email('team_member', f'Under usage detected for data endpoint "{c.m.endpoint_identifier}"')

  @when_all(m.days_since_last_access >= 90)
  def inactive_resource(c):
    send_email('user', f'Files on endpoint "{c.m.endpoint_identifier}" have not been accessed in the last 90')
  
  # prevent MessageNotHandledException if no rule is activated
  @when_all(+m.endpoint_identifier)
  def no_match(c):
    print(f'No rules activated for endpoint {c.m.endpoint_identifier}')

endpoints = [
  DataEndpoint('endpoint-0', 512, 104, 'team1@email.com', '2025-05-01'),
  DataEndpoint('endpoint-1', 100, 135, 'team2@email.com', '2024-08-12'),  # last access mora than 90 days ago
  DataEndpoint('endpoint-2', 512, 404, 'team3@email.com', '2024-12-25'),  # last access mora than 90 days ago
  DataEndpoint('endpoint-3', 512, 5, 'team4@email.com', '2025-02-28'),    # less than 20% usage
  DataEndpoint('endpoint-4', 512, 304, 'team5@email.com', '2025-03-11')
]

for endpoint in endpoints:
  post('data_endpoint', asdict(endpoint))