## Data graph

In preparation for the check-in of
[Innopolis University](https://innopolis.university/) applicants at
[InnoBootCamp 2023](https://t.me/universityinnopolis/885), we collected a data
graph showing the relationship between participants, questions, and answers. We
have also included the result of the applicant distribution by room in this
graph.

The graph is presented as three files:

- [participants.json](./datagraph/participants.json) - a list of participants.
- [fields.json](./datagraph/fields.json) - a list of single-choice questions.
- [answers.json](./datagraph/answers.json) - a list of answers to the questions.

Below you will find a description of each node stored in the data graph.

### Participant

This node represents a Randorm user.

#### Model

| Field              | Type             | Required | Description                                                                                                            |
| ------------------ | ---------------- | -------- | ---------------------------------------------------------------------------------------------------------------------- |
| created_at         | String           | Yes      |                                                                                                                        |
| id                 | Integer          | Yes      | Unique participant identifier.                                                                                         |
| created_at         | Integer          | Yes      | Date the user was registered. The date is in `"days until deadline"` format.                                           |
| gender             | String           | Yes      | User gender. Can be either `male` or `female`.                                                                         |
| subscriber_count   | Integer          | Yes      | Number of subscribers. **Note** that the value may be higher than the number of identifiers in _subscriber_ids_.       |
| subscriber_ids     | Array of Integer | Yes      | Set of unique subscriber identifiers. **Note** that only users who meet the distribution requirements are presented.   |
| subscription_count | Integer          | Yes      | Number of subscriptions. **Note** that the value may be higher than the number of identifiers in _subscription_ids_.   |
| subscription_ids   | Array of Integer | Yes      | Set of unique subscription identifiers. **Note** that only users who meet the distribution requirements are presented. |
| viewed_count       | Integer          | Yes      | Number of viewed users. **Note** that the value may be higher than the number of identifiers in _viewed_ids_.          |
| viewed_ids         | Array of Integer | Yes      | Set of unique viewed user identifiers. **Note** that only users who meet the distribution requirements are presented.  |
| views              | Integer          | Yes      | Number of views by other users. **Note** that users may have looked more than once.                                    |
| roommate_ids       | Array of Integer | Yes      | Set of unique roommate identifiers.                                                                                    |

> **Note** that participant is anonymized, i.e. participant identifier does
> **NOT** match the real user identifier in the system.

#### Example

```jsonc
{
  "id": 42,
  "created_at": 12,
  "gender": "male",
  "subscriber_count": 14,
  "subscriber_ids": [
    169,
    65,
    120
    // ...
  ],
  "subscription_count": 4,
  "subscription_ids": [
    169,
    65,
    120
    // ...
  ],
  "viewed_count": 4,
  "viewed_ids": [
    169,
    65,
    120
    // ...
  ],
  "views": 59,
  "roommate_ids": [
    128,
    46,
    120
  ]
}
```

### Field

This node represents a single-choice question.

#### Model

| Field    | Type    | Required | Description               |
| -------- | ------- | -------- | ------------------------- |
| id       | Integer | Yes      | Unique field identifier.  |
| question | String  | Yes      | Question.                 |
| options  | Array   | Yes      | Set of options to choose. |

> **Note** that you are only given single-choice questions. No text or
> multiple-choice questions are provided.

#### Example

```jsonc
{
  "id": 3,
  "question": "I'd like a roommate...",
  "options": [
    "Similar to my preferences",
    "Opposite to my preferences"
  ]
}
```

### Answer

This node represents a participant's answer to a single-choice question.

#### Model

| Field         | Type    | Required | Description                    |
| ------------- | ------- | -------- | ------------------------------ |
| field_id      | Integer | Yes      | Unique field identifier.       |
| respondent_id | Integer | Yes      | Unique participant identifier. |
| option        | Integer | Yes      | Chosen option index.           |

> **Note** that some users did not answer the questions because they joined
> late.

#### Example

```jsonc
{
  "field_id": 3,
  "respondent_id": 42,
  "option": 0
}
```
