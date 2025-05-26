from datetime import datetime
from dataclasses import dataclass

from business_rules.engine import run_all
from business_rules.variables import BaseVariables, numeric_rule_variable
from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC


@dataclass
class DataEndpoint:
  endpoint_identifier: str
  space_quota: int
  space_used: int
  associated_email: str
  last_access: datetime


class DataEndpointVariables(BaseVariables):

  def __init__(self, data_endpoint: DataEndpoint):
    self.endpoint = data_endpoint

  @numeric_rule_variable
  def current_usage_percentage(self) -> float:
    return (self.endpoint.space_used * 100) / self.endpoint.space_quota
  
  @numeric_rule_variable
  def days_since_last_access(self) -> int:
    return (datetime.now() - self.endpoint.last_access).days


class DataEndpointActions(BaseActions):

  def __init__(self, endpoint_identifier: str):
    self.cis_storage_email = 'team_mender@email.com'
    self.endpoint = endpoint_identifier
    self.evaluation_result = None
  
  def send_email_notification(self, destination, message) -> None:
    print(f"Sending e-mail to '{destination}' regarding '{message}'")

  @rule_action()
  def under_usage_resource(self) -> None:
    self.send_email_notification('team_member', f'Under usage detected for data endpoint "{self.endpoint}"')
  
  @rule_action(params={'inactive_days': FIELD_NUMERIC})
  def inactive_resource(self, inactive_days) -> None:
    self.send_email_notification('user', f'Files on endpoint "{self.endpoint}" have not been accessed in the last {inactive_days}')


rules = [
  # current_use_percentage < 20
  {
    'conditions': {
      'any': [
        {'name': 'current_usage_percentage', 'operator': 'less_than_or_equal_to', 'value': 20},
      ]
    },
    'actions': [
      # notify team
      {'name': 'under_usage_resource'}
    ]
  },
  # days_since_last_access >= 90
  {
    'conditions': {
      'any': [
        { 'name': 'days_since_last_access', 'operator': 'greater_than_or_equal_to', 'value': 90 },
      ]
    },
    'actions': [
      # notify user
      { 'name': 'inactive_resource', 'params': {'inactive_days': 90} }
    ]
  }
]

endpoints = [
  DataEndpoint('endpoint-0', 512, 104, 'team1@email.com', datetime(2025, 5, 1)),
  DataEndpoint('endpoint-1', 512, 304, 'team5@email.com', datetime(2025, 3, 11)),
  DataEndpoint('endpoint-2', 100, 135, 'team2@email.com', datetime(2024, 8, 12)),   # last access mora than 90 days ago
  DataEndpoint('endpoint-3', 512, 404, 'team3@email.com', datetime(2024, 12, 25)),  # last access mora than 90 days ago
  DataEndpoint('endpoint-4', 512, 5, 'team4@email.com', datetime(2025, 2, 28))      # less than 20% usage
]

for endpoint in endpoints:
  actions = DataEndpointActions(endpoint.endpoint_identifier)
  run_all(
    rule_list=rules,
    defined_variables=DataEndpointVariables(endpoint),
    defined_actions=actions
  )