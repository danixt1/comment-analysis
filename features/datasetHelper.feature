Feature: Test helper

    Scenario: return data without none
        Given content to insert in dataset
            | message   | type      | behavior  | spam  | problems  | comment       |
            | test      | comment   | neutral   | false | 0         | it's a test   |
        When dataset helper receive the text
        Then data is returned without none in value