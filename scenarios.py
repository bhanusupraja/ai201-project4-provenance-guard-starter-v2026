"""
What your test runs. <- UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it.

Criterion 4 (appeal) is NOT in this file: it cannot be tested by sending
text alone — it needs a submission first and then an appeal against the
content_id that came back. It was tested by hand instead (see README,
Run Log and Verdicts): 10 submissions, 10 appeals, each checked in
GET /log for status under_review and an appeal entry.

The 10 "my own writing" texts in criterion 1 are pieces written for
this project in the student's voice for calibration in units 7 and 8.
They are the test set the verdict is measured on; swapping in the
student's own diary or coursework writing is the honest next step
before claiming the rate about anyone else's writing.
"""

AI_GENERIC = (
    "The implementation of the proposed framework requires careful "
    "consideration of several key factors. First, it is important to "
    "note that the system must be able to handle a wide variety of "
    "different inputs. Additionally, the overall performance of the "
    "solution depends on a number of important variables."
)
AI_SYSWORKS = (
    "The system works well. It handles most cases correctly and provides "
    "good results. Users generally find it easy to use and understand. "
    "The system works well for many different tasks and provides good "
    "results for users."
)
AI_FASTPACED = (
    "In today's fast-paced world, it is important to consider the impact "
    "of technology on our daily lives. Many people use their phones "
    "every day to stay connected with friends and family. Technology "
    "has changed the way we work, learn, and communicate with each other."
)
HUMAN_DIWALI = (
    "Last Diwali, my cousin Ravi burnt the payasam. Not a little burnt, "
    "properly charcoal, smoke alarm screaming, and my grandmother just "
    "laughed and said the ancestors liked it smoky anyway, then scraped "
    "the top off and served it in the steel bowls we only use when the "
    "whole family is home, all eleven of us crammed around one table."
)
HUMAN_TRAIN = (
    "I woke at five. The train was late again, forty minutes this time, "
    "and the platform smelled of rain and fried onions from the stall by "
    "the gate. My sister had texted at midnight, three words, no "
    "punctuation, and I still had not answered her by the time the "
    "doors finally opened."
)
HUMAN_POEM = (
    "The moon rose over the quiet harbour, and for a moment nobody spoke. "
    "Then the old fisherman laughed, a short surprised sound, and pointed "
    "at the water, where the light was breaking into a hundred small "
    "pieces, each one different, each one gone before you could count it."
)
HUMAN_ORNATE = (
    "Beneath the cracked lintel, where the monsoon had peeled the paint "
    "into curls like old parchment, Amma kept her brass lamps polished "
    "to a mirror sheen, muttering prayers in a dialect no textbook had "
    "ever bothered to record, while the jackfruit tree outside dropped "
    "its heavy fruit with a thud that shook the tin roof at odd hours."
)
HUMAN_FRAGMENT = (
    "Rain. Again. The bus never came, so I walked, shoes squeaking, "
    "umbrella inside-out by the second corner. By the time I reached "
    "the library my notes were damp, my hair was flat, and the "
    "librarian, Mrs. Rao, just pointed at the radiator without saying "
    "a word, like she had seen this exact disaster a hundred times before."
)
HUMAN_WALK = (
    "I like to go for a walk in the morning. I walk to the park near my "
    "house. I see many people there. They walk their dogs and talk to "
    "each other. It is a nice way to start the day. I come home and make "
    "tea. Then I sit down and read my book for a while."
)
HUMAN_WINTER = (
    "My favourite season is winter. In winter it is cold and we wear "
    "warm clothes. I like to drink hot chocolate and sit near the "
    "window. My family goes to my grandmother's house in winter. We eat "
    "good food and play games together. Winter is the best season for me."
)
HUMAN_SUNPOEM = (
    "The sun comes up. The birds sing. I open my window and breathe in "
    "the morning air. The day is new and the sky is blue. I am happy to "
    "be alive and I am ready to begin."
)
HUMAN_RECIPE = (
    "First, take two cups of rice and wash it well. Then put it in a pot "
    "with four cups of water. Add a little salt and cook it on a low "
    "flame for twenty minutes. When it is done, turn off the stove and "
    "let it sit for five minutes. Serve it hot with dal."
)
HUMAN_NOTE = (
    "Hi Priya. I hope you are doing well. I am writing to say thank you "
    "for the book. I liked it very much. I finished it last night. Let "
    "us meet for coffee this weekend. I will bring the book back then. "
    "Take care."
)
BORDERLINE_PARAPHRASE = (
    "Putting this framework into practice means thinking hard about a "
    "handful of central issues. To begin with, the platform has to cope "
    "with many kinds of input, not just one. On top of that, how well "
    "the whole thing performs comes down to several significant factors "
    "working together."
)

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        "texts": [
            HUMAN_DIWALI,
            HUMAN_TRAIN,
            HUMAN_POEM,
            HUMAN_ORNATE,
            HUMAN_FRAGMENT,
            HUMAN_WALK,
            HUMAN_WINTER,
            HUMAN_SUNPOEM,
            HUMAN_RECIPE,
            HUMAN_NOTE,
        ],
    },
    {
        "name": "score spread",
        "criterion": 2,
        "texts": [
            AI_GENERIC,
            AI_SYSWORKS,
            AI_FASTPACED,
            HUMAN_DIWALI,
            HUMAN_ORNATE,
            HUMAN_FRAGMENT,
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "texts": [
            AI_GENERIC,
            AI_SYSWORKS,
            AI_FASTPACED,
            HUMAN_DIWALI,
            HUMAN_ORNATE,
            HUMAN_FRAGMENT,
            HUMAN_TRAIN,
            HUMAN_POEM,
            BORDERLINE_PARAPHRASE,
        ],
    },
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"creator_id": "eval_bad_missing"},
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": "word " * 5000, "creator_id": "eval_bad_huge"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
