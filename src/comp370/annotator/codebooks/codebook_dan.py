from comp370.annotator.codebook import Codebook
from comp370.annotator.codebook import Category
from comp370.annotator.codebook import Example

CODEBOOK = Codebook(
    name="Seinfeld dialogue topics codebook",
    description="A codebook for categorizing Seinfeld dialogue lines based on conversation topics.",
    categories=[
        Category(
            name="Food",
            description="Lines about food, restaurants, eating, meals, or dining experiences.",
            examples=[
                Example(
                    input="I can't believe they're out of marble rye!",
                    include=True,
                    why="This line discusses a specific food item.",
                ),
                Example(
                    input="The soup at this place is amazing, but the guy is a total Nazi.",
                    include=True,
                    why="This line is about a restaurant and dining experience.",
                ),
                Example(
                    input="Let's grab lunch at Monk's.",
                    include=True,
                    why="This line involves dining plans.",
                ),
                Example(
                    input="I'm so tired today.",
                    include=False,
                    why="This line does not involve food or dining.",
                ),
            ],
        ),
        Category(
            name="Relationships",
            description="Lines about romantic relationships, dating, breakups, attraction, or relationship dynamics.",
            examples=[
                Example(
                    input="She's got man hands!",
                    include=True,
                    why="This line discusses a physical attribute in a dating context.",
                ),
                Example(
                    input="I think I'm in love with her.",
                    include=True,
                    why="This line involves romantic feelings.",
                ),
                Example(
                    input="My girlfriend broke up with me because I wouldn't try her pie.",
                    include=True,
                    why="This line discusses a relationship issue.",
                ),
                Example(
                    input="I need to call my mother back.",
                    include=False,
                    why="This line is about family, not romantic relationships.",
                ),
            ],
        ),
        Category(
            name="Work",
            description="Lines about jobs, employment, workplace situations, bosses, coworkers, or career matters.",
            examples=[
                Example(
                    input="Steinbrenner wants to see me in his office.",
                    include=True,
                    why="This line discusses a workplace situation.",
                ),
                Example(
                    input="I pretended to be an architect to impress her.",
                    include=True,
                    why="This line involves career/employment in context.",
                ),
                Example(
                    input="If I don't finish this project, I'm getting fired.",
                    include=True,
                    why="This line discusses employment consequences.",
                ),
                Example(
                    input="I'm going to the movies tonight.",
                    include=False,
                    why="This line does not involve work matters.",
                ),
            ],
        ),
        Category(
            name="Money",
            description="Lines about money, costs, prices, financial transactions, deals, or economic matters.",
            examples=[
                Example(
                    input="How much did you pay for that jacket?",
                    include=True,
                    why="This line asks about cost.",
                ),
                Example(
                    input="I got a great deal on this car!",
                    include=True,
                    why="This line discusses a financial transaction.",
                ),
                Example(
                    input="My rent is due tomorrow and I'm broke.",
                    include=True,
                    why="This line involves money and expenses.",
                ),
                Example(
                    input="I love that show!",
                    include=False,
                    why="This line does not involve financial matters.",
                ),
            ],
        ),
        Category(
            name="Lifestyle",
            description="Lines about apartments, living situations, neighborhoods, New York locations, or city life.",
            examples=[
                Example(
                    input="There's a guy living across the hall who never wears a shirt.",
                    include=True,
                    why="This line discusses apartment living situation.",
                ),
                Example(
                    input="I know a great parking spot on 84th Street.",
                    include=True,
                    why="This line references a New York location.",
                ),
                Example(
                    input="My apartment is rent-controlled.",
                    include=True,
                    why="This line discusses housing situation.",
                ),
                Example(
                    input="I'm thinking about what to have for breakfast.",
                    include=False,
                    why="This line does not involve locations or living situations.",
                ),
            ],
        ),
        Category(
            name="Culture",
            description="Lines about TV shows, movies, sports, celebrities, or popular culture references.",
            examples=[
                Example(
                    input="Did you see the Mets game last night?",
                    include=True,
                    why="This line references a sports event.",
                ),
                Example(
                    input="That movie was based on my life!",
                    include=True,
                    why="This line discusses a film.",
                ),
                Example(
                    input="She looks like Lois Lane.",
                    include=True,
                    why="This line makes a pop culture reference.",
                ),
                Example(
                    input="I need to go to the dentist.",
                    include=False,
                    why="This line does not involve entertainment or culture.",
                ),
            ],
        ),
        Category(
            name="Health",
            description="Lines about medical issues, doctors, physical conditions, illnesses, or bodily concerns.",
            examples=[
                Example(
                    input="My back is killing me!",
                    include=True,
                    why="This line discusses a physical condition.",
                ),
                Example(
                    input="I have an appointment with my doctor tomorrow.",
                    include=True,
                    why="This line involves medical matters.",
                ),
                Example(
                    input="I think I'm going bald.",
                    include=True,
                    why="This line discusses a bodily concern.",
                ),
                Example(
                    input="I'm going to the store.",
                    include=False,
                    why="This line does not involve health or body matters.",
                ),
            ],
        ),
        Category(
            name="Miscellaneous",
            description="Lines that don't fit into any other specific topic category, including general statements, greetings, and uncategorizable content.",
            examples=[
                Example(
                    input="Hello!",
                    include=True,
                    why="This is a simple greeting that doesn't fit other categories.",
                ),
                Example(
                    input="What time is it?",
                    include=True,
                    why="This is a general question that doesn't relate to specific topics.",
                ),
                Example(
                    input="That's interesting.",
                    include=True,
                    why="This is a vague statement that doesn't fit other categories.",
                ),
                Example(
                    input="I can't believe they're out of marble rye!",
                    include=False,
                    why="This line clearly belongs in Food & Dining category.",
                ),
            ],
        ),
    ],
)
