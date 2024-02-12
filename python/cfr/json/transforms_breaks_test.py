"""Tests for break rule transformations."""

import copy
import datetime
import unittest

from . import cfr_json
from . import transforms_breaks


class TransformBreaksTest(unittest.TestCase):
  """Tests for transform_breaks."""

  maxDiff = None

  def run_transform_breaks(
      self, model: cfr_json.ShipmentModel, rules: str
  ) -> cfr_json.ShipmentModel:
    """A shortcut method that compiles `rules` and applies them to `model`."""
    compiled_rules = transforms_breaks.compile_rules(rules)
    model = copy.deepcopy(model)
    transforms_breaks.transform_breaks(model, compiled_rules)
    return model

  def test_delete_break_request(self):
    model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "breakRule": {
                "breakRequests": [
                    {
                        "earliestStartTime": "2024-02-09T11:30:00Z",
                        "latestStartTime": "2024-02-09T12:30:00Z",
                        "minDuration": "3600s",
                    },
                    {
                        "earliestStartTime": "2024-02-09T14:00:00Z",
                        "latestStartTime": "2024-02-09T16:00:00Z",
                        "minDuration": "3600s",
                    },
                ]
            }
        }],
    }
    expected_model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "breakRule": {
                "breakRequests": [
                    {
                        "earliestStartTime": "2024-02-09T11:30:00Z",
                        "latestStartTime": "2024-02-09T12:30:00Z",
                        "minDuration": "3600s",
                    },
                ]
            }
        }],
    }
    self.assertEqual(
        self.run_transform_breaks(model, "@time=14:00:00 delete"),
        expected_model,
    )

  def test_return_to_depot(self):
    model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "startWaypoint": {"placeId": "foobar"},
            "breakRule": {
                "breakRequests": [
                    {
                        "earliestStartTime": "2024-02-09T11:30:00Z",
                        "latestStartTime": "2024-02-09T12:30:00Z",
                        "minDuration": "3600s",
                    },
                    {
                        "earliestStartTime": "2024-02-09T14:00:00Z",
                        "latestStartTime": "2024-02-09T16:00:00Z",
                        "minDuration": "3600s",
                    },
                ]
            },
        }],
    }
    expected_model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "startWaypoint": {"placeId": "foobar"},
            "breakRule": {
                "breakRequests": [
                    {
                        "earliestStartTime": "2024-02-09T11:30:00Z",
                        "latestStartTime": "2024-02-09T12:30:00Z",
                        "minDuration": "3600s",
                    },
                ]
            },
        }],
        "shipments": [{
            "allowedVehicleIndices": [0],
            "label": "break, vehicle_index=0",
            "deliveries": [{
                "arrivalWaypoint": {"placeId": "foobar"},
                "timeWindows": [{
                    "startTime": "2024-02-09T14:00:00Z",
                    "endTime": "2024-02-09T16:00:00Z",
                }],
                "duration": "3600s",
            }],
        }],
    }
    self.assertEqual(
        self.run_transform_breaks(model, "@time=14:00:00 depot"),
        expected_model,
    )

  def test_all_return_to_depot(self):
    model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "startWaypoint": {"placeId": "foobar"},
            "breakRule": {
                "breakRequests": [
                    {
                        "earliestStartTime": "2024-02-09T11:30:00Z",
                        "latestStartTime": "2024-02-09T12:30:00Z",
                        "minDuration": "3600s",
                    },
                    {
                        "earliestStartTime": "2024-02-09T14:00:00Z",
                        "latestStartTime": "2024-02-09T16:00:00Z",
                        "minDuration": "3600s",
                    },
                ]
            },
        }],
    }
    expected_model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "startWaypoint": {"placeId": "foobar"},
        }],
        "shipments": [
            {
                "allowedVehicleIndices": [0],
                "label": "break, vehicle_index=0",
                "deliveries": [{
                    "arrivalWaypoint": {"placeId": "foobar"},
                    "timeWindows": [{
                        "startTime": "2024-02-09T11:30:00Z",
                        "endTime": "2024-02-09T12:30:00Z",
                    }],
                    "duration": "3600s",
                }],
            },
            {
                "allowedVehicleIndices": [0],
                "label": "break, vehicle_index=0",
                "deliveries": [{
                    "arrivalWaypoint": {"placeId": "foobar"},
                    "timeWindows": [{
                        "startTime": "2024-02-09T14:00:00Z",
                        "endTime": "2024-02-09T16:00:00Z",
                    }],
                    "duration": "3600s",
                }],
            },
        ],
    }
    self.assertEqual(
        self.run_transform_breaks(model, "depot"),
        expected_model,
    )

  def test_new_request(self):
    model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "breakRule": {
                "breakRequests": [
                    {
                        "earliestStartTime": "2024-02-09T11:30:00Z",
                        "latestStartTime": "2024-02-09T12:30:00Z",
                        "minDuration": "3600s",
                    },
                    {
                        "earliestStartTime": "2024-02-09T14:00:00Z",
                        "latestStartTime": "2024-02-09T16:00:00Z",
                        "minDuration": "3600s",
                    },
                ]
            }
        }],
    }
    expected_model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [{
            "breakRule": {
                "breakRequests": [
                    {
                        "earliestStartTime": "2024-02-09T11:30:00Z",
                        "latestStartTime": "2024-02-09T12:30:00Z",
                        "minDuration": "3600s",
                    },
                    {
                        "earliestStartTime": "2024-02-09T13:00:00Z",
                        "latestStartTime": "2024-02-09T13:30:00Z",
                        "minDuration": "600s",
                    },
                    {
                        "earliestStartTime": "2024-02-09T14:00:00Z",
                        "latestStartTime": "2024-02-09T16:00:00Z",
                        "minDuration": "3600s",
                    },
                ]
            }
        }],
    }
    self.assertEqual(
        self.run_transform_breaks(
            model,
            """
            @time=12:00:00 new
              earliestStartTime=13:00:00
              latestStartTime=13:30:00
              minDuration=600s""",
        ),
        expected_model,
    )

  def test_new_return_to_depot(self):
    model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0001",
                "breakRule": {
                    "breakRequests": [{
                        "earliestStartTime": "2024-02-09T14:00:00Z",
                        "latestStartTime": "2024-02-09T16:00:00Z",
                        "minDuration": "3600s",
                    }]
                },
            },
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0002",
            },
        ],
    }
    expected_model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "shipments": [
            {
                "allowedVehicleIndices": [0],
                "deliveries": [{
                    "arrivalWaypoint": {"placeId": "foo123"},
                    "duration": "600s",
                    "timeWindows": [{
                        "endTime": "2024-02-09T13:30:00Z",
                        "startTime": "2024-02-09T13:00:00Z",
                    }],
                }],
                "label": "break, vehicle_index=0, vehicle_label='V0001'",
            },
            {
                "allowedVehicleIndices": [1],
                "deliveries": [{
                    "arrivalWaypoint": {"placeId": "foo123"},
                    "duration": "600s",
                    "timeWindows": [{
                        "endTime": "2024-02-09T13:30:00Z",
                        "startTime": "2024-02-09T13:00:00Z",
                    }],
                }],
                "label": "break, vehicle_index=1, vehicle_label='V0002'",
            },
        ],
        "vehicles": [
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0001",
                "breakRule": {
                    "breakRequests": [{
                        "earliestStartTime": "2024-02-09T14:00:00Z",
                        "latestStartTime": "2024-02-09T16:00:00Z",
                        "minDuration": "3600s",
                    }]
                },
            },
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0002",
            },
        ],
    }
    self.assertEqual(
        self.run_transform_breaks(
            model,
            """
            new
              earliestStartTime=13:00:00
              latestStartTime=13:30:00
              minDuration=600s
              depot
            """,
        ),
        expected_model,
    )

  def test_conditional_new_return_to_depot(self):
    model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "vehicles": [
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0001",
                "breakRule": {
                    "breakRequests": [
                        {
                            "earliestStartTime": "2024-02-09T11:30:00Z",
                            "latestStartTime": "2024-02-09T12:30:00Z",
                            "minDuration": "3600s",
                        },
                        {
                            "earliestStartTime": "2024-02-09T14:00:00Z",
                            "latestStartTime": "2024-02-09T16:00:00Z",
                            "minDuration": "3600s",
                        },
                    ]
                },
            },
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0002",
                "breakRule": {
                    "breakRequests": [
                        {
                            "earliestStartTime": "2024-02-09T11:30:00Z",
                            "latestStartTime": "2024-02-09T12:30:00Z",
                            "minDuration": "3600s",
                        },
                        {
                            "earliestStartTime": "2024-02-09T14:00:00Z",
                            "latestStartTime": "2024-02-09T16:00:00Z",
                            "minDuration": "3600s",
                        },
                    ]
                },
            },
            {
                "label": "V0003",
            },
        ],
    }
    expected_model: cfr_json.ShipmentModel = {
        "globalStartTime": "2024-02-09T08:00:00Z",
        "globalEndTime": "2024-02-09T18:00:00Z",
        "shipments": [
            {
                "allowedVehicleIndices": [0],
                "deliveries": [{
                    "arrivalWaypoint": {"placeId": "foo123"},
                    "duration": "600s",
                    "timeWindows": [{
                        "endTime": "2024-02-09T13:30:00Z",
                        "startTime": "2024-02-09T13:00:00Z",
                    }],
                }],
                "label": "break, vehicle_index=0, vehicle_label='V0001'",
            },
            {
                "allowedVehicleIndices": [1],
                "deliveries": [{
                    "arrivalWaypoint": {"placeId": "foo123"},
                    "duration": "600s",
                    "timeWindows": [{
                        "endTime": "2024-02-09T13:30:00Z",
                        "startTime": "2024-02-09T13:00:00Z",
                    }],
                }],
                "label": "break, vehicle_index=1, vehicle_label='V0002'",
            },
        ],
        "vehicles": [
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0001",
                "breakRule": {
                    "breakRequests": [
                        {
                            "earliestStartTime": "2024-02-09T11:30:00Z",
                            "latestStartTime": "2024-02-09T12:30:00Z",
                            "minDuration": "3600s",
                        },
                        {
                            "earliestStartTime": "2024-02-09T14:00:00Z",
                            "latestStartTime": "2024-02-09T16:00:00Z",
                            "minDuration": "3600s",
                        },
                    ]
                },
            },
            {
                "startWaypoint": {"placeId": "foo123"},
                "label": "V0002",
                "breakRule": {
                    "breakRequests": [
                        {
                            "earliestStartTime": "2024-02-09T11:30:00Z",
                            "latestStartTime": "2024-02-09T12:30:00Z",
                            "minDuration": "3600s",
                        },
                        {
                            "earliestStartTime": "2024-02-09T14:00:00Z",
                            "latestStartTime": "2024-02-09T16:00:00Z",
                            "minDuration": "3600s",
                        },
                    ]
                },
            },
            {
                "label": "V0003",
            },
        ],
    }
    self.assertEqual(
        self.run_transform_breaks(
            model,
            # Add a new break at the depot starting at 13:00-13:30 of at least
            # 600s, but only when there is a break at 12:00.
            """
            @time=12:00:00 new
              earliestStartTime=13:00:00
              latestStartTime=13:30:00
              minDuration=600s
              depot
            """,
        ),
        expected_model,
    )


class CompileRulesTest(unittest.TestCase):
  maxDiff = None

  MODEL: cfr_json.ShipmentModel = {
      "globalStartTime": "2024-02-09T08:00:00Z",
      "globalEndTime": "2024-02-09T18:00:00Z",
  }
  VEHICLE: cfr_json.Vehicle = {}

  def test_set_start_end_time(self):
    rules = transforms_breaks.compile_rules(
        "earliestStartTime=08:00:00 latestStartTime=17:00:00"
    )
    self.assertEqual(len(rules), 1)
    break_request: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-09T12:00:00Z",
        "latestStartTime": "2024-02-09T13:00:00Z",
        "minDuration": "3600s",
    }
    self.assertTrue(rules[0].applies_to(break_request))
    transformed_breaks = rules[0].apply_to(
        self.MODEL, self.VEHICLE, break_request
    )
    self.assertSequenceEqual(
        transformed_breaks,
        (
            {
                "earliestStartTime": "2024-02-09T08:00:00Z",
                "latestStartTime": "2024-02-09T17:00:00Z",
                "minDuration": "3600s",
            },
        ),
    )

  def test_set_start_end_time_with_selector(self):
    rules = transforms_breaks.compile_rules("""
        @time=12:00:00
          earliestStartTime=08:00:00
          latestStartTime=17:00:00;
        @time=16:00:00 earliestStartTime=15:00:00
        """)
    self.assertEqual(len(rules), 2)

    noon_break: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-09T12:00:00Z",
        "latestStartTime": "2024-02-09T13:00:00Z",
        "minDuration": "3600s",
    }
    self.assertTrue(rules[0].applies_to(noon_break))
    self.assertFalse(rules[1].applies_to(noon_break))
    self.assertSequenceEqual(
        rules[0].apply_to(self.MODEL, self.VEHICLE, noon_break),
        (
            {
                "earliestStartTime": "2024-02-09T08:00:00Z",
                "latestStartTime": "2024-02-09T17:00:00Z",
                "minDuration": "3600s",
            },
        ),
    )

    afternoon_break: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-09T12:30:00Z",
        "latestStartTime": "2024-02-09T16:00:00Z",
        "minDuration": "150s",
    }
    self.assertFalse(rules[0].applies_to(afternoon_break))
    self.assertTrue(rules[1].applies_to(afternoon_break))
    self.assertSequenceEqual(
        rules[1].apply_to(self.MODEL, self.VEHICLE, afternoon_break),
        (
            {
                "earliestStartTime": "2024-02-09T15:00:00Z",
                "latestStartTime": "2024-02-09T16:00:00Z",
                "minDuration": "150s",
            },
        ),
    )

  def test_set_min_duration(self):
    rules = transforms_breaks.compile_rules("minDuration=60s")
    self.assertEqual(len(rules), 1)

    break_request: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-09T12:00:00Z",
        "latestStartTime": "2024-02-09T13:00:00Z",
        "minDuration": "3600s",
    }
    self.assertTrue(rules[0].applies_to(break_request))
    self.assertSequenceEqual(
        rules[0].apply_to(self.MODEL, self.VEHICLE, break_request),
        (
            {
                "earliestStartTime": "2024-02-09T12:00:00Z",
                "latestStartTime": "2024-02-09T13:00:00Z",
                "minDuration": "60s",
            },
        ),
    )

  def test_no_rules(self):
    rules = transforms_breaks.compile_rules("")
    self.assertEqual(len(rules), 0)

  def test_empty_rules(self):
    rules = transforms_breaks.compile_rules(";minDuration=60s;;")
    self.assertEqual(len(rules), 1)
    break_request: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-09T12:00:00Z",
        "latestStartTime": "2024-02-09T13:00:00Z",
        "minDuration": "3600s",
    }
    self.assertTrue(rules[0].applies_to(break_request))
    self.assertSequenceEqual(
        rules[0].apply_to(self.MODEL, self.VEHICLE, break_request),
        (
            {
                "earliestStartTime": "2024-02-09T12:00:00Z",
                "latestStartTime": "2024-02-09T13:00:00Z",
                "minDuration": "60s",
            },
        ),
    )

  def test_does_not_parse(self):
    with self.assertRaisesRegex(ValueError, "Could not parse component"):
      transforms_breaks.compile_rules("""print("hello world")""")

  def test_invalid_name(self):
    with self.assertRaisesRegex(ValueError, "Unexpected name .foo."):
      transforms_breaks.compile_rules("""foo=bar""")


class ParseTimeTest(unittest.TestCase):
  """Tests for _parse_time."""

  def test_parse_time_success(self):
    test_cases = (
        ("00:00:00", datetime.time()),
        ("01:23:45", datetime.time(1, 23, 45)),
        ("23:59:59", datetime.time(23, 59, 59)),
    )
    for time_str, expected_time in test_cases:
      with self.subTest(time_str=time_str, expected_time=expected_time):
        time = transforms_breaks._parse_time(time_str)
        self.assertEqual(time, expected_time)

  def test_parse_time_failure(self):
    test_cases = (
        "00:00",
        "foo? bar!",
        "foo:bar:baz",
        "-12:00:00",
        "25:00:00",
        "16:61:23",
        "07:00:125",
    )
    for test_case in test_cases:
      with self.subTest(test_case=test_case):
        with self.assertRaises(ValueError):
          transforms_breaks._parse_time(test_case)


class BreakStartTimeWindowContainsTimeTest(unittest.TestCase):
  """Tests for _break_start_time_window_contains_time."""

  def test_break_start_time_window_contains_time(self):
    test_cases = (
        # Single day.
        ("2024-02-09T17:00:00Z", "2024-02-09T22:00:00Z", "18:00:00", True),
        ("2024-02-09T17:00:00Z", "2024-02-09T22:00:00Z", "17:00:00", True),
        ("2024-02-09T17:00:00Z", "2024-02-09T22:00:00Z", "22:00:00", True),
        ("2024-02-09T17:00:00Z", "2024-02-09T22:00:00Z", "16:59:59", False),
        ("2024-02-09T17:00:00Z", "2024-02-09T22:00:00Z", "22:15:00", False),
        # Cross-midnight.
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "22:15:00", True),
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "21:00:00", True),
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "01:32:0", True),
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "02:00:00", True),
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "20:59:59", False),
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "02:00:01", False),
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "12:00:00", False),
        ("2024-02-09T21:00:00Z", "2024-02-10T02:00:00Z", "00:00:00", True),
        # Multi-day.
        ("2024-02-09T17:00:00Z", "2024-02-11T22:00:00Z", "18:00:00", True),
        ("2024-02-09T17:00:00Z", "2024-02-11T22:00:00Z", "17:00:00", True),
        ("2024-02-09T17:00:00Z", "2024-02-11T22:00:00Z", "22:00:00", True),
        ("2024-02-09T17:00:00Z", "2024-02-11T22:00:00Z", "16:59:59", True),
        ("2024-02-09T17:00:00Z", "2024-02-11T22:00:00Z", "22:15:00", True),
    )
    for earliest_start, latest_start, time_str, expected_contains in test_cases:
      with self.subTest(
          earliest_start=earliest_start,
          latest_start=latest_start,
          time=time_str,
          expected_contains=expected_contains,
      ):
        time = transforms_breaks._parse_time(time_str)
        break_request: cfr_json.BreakRequest = {
            "earliestStartTime": earliest_start,
            "latestStartTime": latest_start,
        }
        self.assertEqual(
            transforms_breaks._break_start_time_window_contains_time(
                time, break_request
            ),
            expected_contains,
        )


class SetBreakStartTimeWindowComponentTimeTest(unittest.TestCase):
  """Tests for _set_break_start_time_window_component_time."""

  MODEL: cfr_json.ShipmentModel = {
      "globalStartTime": "2024-02-09T16:00:00Z",
      "globalEndTime": "2024-02-10T04:00:00Z",
  }
  VEHICLE: cfr_json.Vehicle = {}

  maxDiff = None

  def test_set_start_time_same_day(self):
    break_request: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-09T17:00:00Z",
        "latestStartTime": "2024-02-09T19:00:00Z",
    }
    with self.subTest("earliestStartTime"):
      expected_break_request: cfr_json.BreakRequest = {
          "earliestStartTime": "2024-02-09T18:55:00Z",
          "latestStartTime": "2024-02-09T19:00:00Z",
      }
      transformed = (
          transforms_breaks._set_break_start_time_window_component_time(
              "earliestStartTime",
              datetime.time(18, 55, 00),
              self.MODEL,
              self.VEHICLE,
              copy.deepcopy(break_request),
          )
      )
      self.assertSequenceEqual(transformed, (expected_break_request,))
    with self.subTest("latestStartTime"):
      expected_break_request: cfr_json.BreakRequest = {
          "earliestStartTime": "2024-02-09T17:00:00Z",
          "latestStartTime": "2024-02-09T18:55:00Z",
      }
      transformed = (
          transforms_breaks._set_break_start_time_window_component_time(
              "latestStartTime",
              datetime.time(18, 55, 0),
              self.MODEL,
              self.VEHICLE,
              copy.deepcopy(break_request),
          )
      )
      self.assertSequenceEqual(transformed, (expected_break_request,))

  def test_set_start_time_next_day(self):
    break_request: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-09T17:00:00Z",
        "latestStartTime": "2024-02-09T19:00:00Z",
    }
    with self.subTest("latestStartTime"):
      expected_break_request: cfr_json.BreakRequest = {
          "earliestStartTime": "2024-02-09T17:00:00Z",
          "latestStartTime": "2024-02-10T03:00:00Z",
      }
      transformed = (
          transforms_breaks._set_break_start_time_window_component_time(
              "latestStartTime",
              datetime.time(3, 0, 0),
              self.MODEL,
              self.VEHICLE,
              break_request,
          )
      )
      self.assertSequenceEqual(transformed, (expected_break_request,))
    with self.subTest("earliestStartTime"):
      expected_break_request: cfr_json.BreakRequest = {
          "earliestStartTime": "2024-02-10T01:23:45Z",
          "latestStartTime": "2024-02-10T03:00:00Z",
      }
      transformed = (
          transforms_breaks._set_break_start_time_window_component_time(
              "earliestStartTime",
              datetime.time(1, 23, 45),
              self.MODEL,
              self.VEHICLE,
              break_request,
          )
      )
      self.assertSequenceEqual(transformed, (expected_break_request,))

  def test_set_start_time_previous_day(self):
    break_request: cfr_json.BreakRequest = {
        "earliestStartTime": "2024-02-10T00:00:00Z",
        "latestStartTime": "2024-02-10T03:00:00Z",
    }
    with self.subTest("earliestStartTime"):
      expected_break_request: cfr_json.BreakRequest = {
          "earliestStartTime": "2024-02-09T16:00:00Z",
          "latestStartTime": "2024-02-10T03:00:00Z",
      }
      transformed = (
          transforms_breaks._set_break_start_time_window_component_time(
              "earliestStartTime",
              datetime.time(16, 0, 0),
              self.MODEL,
              self.VEHICLE,
              break_request,
          )
      )
      self.assertSequenceEqual(transformed, (expected_break_request,))
    with self.subTest("latestStartTime"):
      expected_break_request: cfr_json.BreakRequest = {
          "earliestStartTime": "2024-02-09T16:00:00Z",
          "latestStartTime": "2024-02-09T23:59:59Z",
      }
      transformed = (
          transforms_breaks._set_break_start_time_window_component_time(
              "latestStartTime",
              datetime.time(23, 59, 59),
              self.MODEL,
              self.VEHICLE,
              break_request,
          )
      )
      self.assertSequenceEqual(transformed, (expected_break_request,))


if __name__ == "__main__":
  unittest.main()
