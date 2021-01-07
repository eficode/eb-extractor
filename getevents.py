#!/usr/bin/env python

import argparse
import json
import datetime

import requests

from collections import namedtuple
from typing import Dict, List, Tuple

attendee = namedtuple("attendee", ["name", "email"])


class Event:
    def __init__(self, *, event: Dict, token: str) -> None:
        self.event = event
        self.token = token

    def __str__(self):
        return f"{self.event['name']['text']}, {self.event['start']['local']}"

    def get_attendees(self, only_eficode=False, token=None) -> List[namedtuple]:
        fetch_more = True
        continuation = ""
        attendees = []  # type: List[Tuple[str, str]]
        while fetch_more:
            resp = requests.get(
                f"https://www.eventbriteapi.com/v3/events/{self.event['id']}/attendees/?continuation={continuation}",
                headers={"Authorization": f"Bearer {token}"},
            )
            decoder = json.JSONDecoder()
            data = decoder.decode(resp.text)
            try:
                for a in data["attendees"]:
                    try:
                        email = a["profile"]["email"]
                        if only_eficode:
                            if "eficode" not in email[email.index('@') + 1:]:
                                continue
                        if a["status"] != "Attending":
                            continue
                        attendees.append(
                            attendee._make([
                                " ".join([a["profile"]["first_name"], a["profile"]["last_name"]]),
                                email,
                            ]
                        ))
                    except KeyError:
                        # Just for debugging purposes
                        # Eventbrite supports registration without emails
                        print([a["profile"]["first_name"], a["profile"]["last_name"]])
                if data["pagination"]["has_more_items"]:
                    continuation = data["pagination"]["continuation"]
                else:
                    fetch_more = False
            except KeyError:
                print(self.event["name"]["text"])
        return attendees

    def write_file(self, output, only_eficode=False):
        attendees = self.get_attendees(only_eficode=only_eficode, token=self.token)
        with open(output, mode="a+") as f:
            for participant in attendees:
                f.write(";".join([
                    self.event["name"]["text"],
                    self.event["start"]["local"][:10],
                    self.event["end"]["local"][:10],
                    participant.name,
                    participant.email,
                ]) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2020)
    parser.add_argument("--organization", type=str, required=True)
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--only-internal", type=bool, default=False)

    args = parser.parse_args()

    token = args.token
    internal = args.only_internal
    organization_id = args.organization
    continuation = ""
    fetch_more = True
    events = []  # type: List[Event]
    while fetch_more:
        resp = requests.get(
            f"https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/?continuation={continuation}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response = resp.text
        data = json.JSONDecoder().decode(s=response)
        fetch_more = data["pagination"]["has_more_items"]
        if fetch_more:
            continuation = data["pagination"]["continuation"]
        for event in data["events"]:
            d = datetime.datetime.strptime(event["start"]["local"], "%Y-%m-%dT%H:%M:%S")
            if d.year >= args.year:
                events.append(Event(event=event, token=args.token))
    with open(args.output, mode="a+") as f:
        f.write("event name;start date;end date;name;email\n")
    for e in events:
        e.write_file(args.output, only_eficode=internal)


if __name__ == '__main__':
    main()
