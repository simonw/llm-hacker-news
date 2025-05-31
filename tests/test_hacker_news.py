import llm
from llm_hacker_news import hacker_news_loader


def test_hacker_news_loader(httpx_mock):
    httpx_mock.add_response(json=EXAMPLE)
    fragment = hacker_news_loader("123456")
    assert isinstance(fragment, llm.Fragment)
    assert fragment.source == "https://news.ycombinator.com/item?id=123456"
    assert str(fragment) == (
        '[1] BeakMaster: Fish Spotting Techniques\n\n'
        '[1.1] CoastalFlyer: The dive technique works best when hunting in shallow waters.\n\n'
        '[1.1.1] PouchBill: Agreed. Have you tried the hover method near the pier?\n\n'
        '[1.1.2] WingSpan22: My bill gets too wet with that approach.\n\n'
        '[1.1.2.1] CoastalFlyer: Try tilting at a 40° angle like our Australian cousins.\n\n'
        '[1.2] BrownFeathers: Anyone spotted those "silver fish" near the rocks?\n\n'
        '[1.2.1] GulfGlider: Yes! They\'re best caught at dawn.\nJust remember: swoop > grab > lift'
    )


EXAMPLE = {
    "author": "BeakMaster",
    "title": "Fish Spotting Techniques",
    "children": [
        {
            "author": "CoastalFlyer",
            "text": "The dive technique works best when hunting in shallow waters.",
            "children": [
                {
                    "author": "PouchBill",
                    "text": "Agreed. Have you tried the hover method near the pier?",
                    "children": [],
                },
                {
                    "author": "WingSpan22",
                    "text": "My bill gets too wet with that approach.",
                    "children": [
                        {
                            "author": "CoastalFlyer",
                            "text": "Try tilting at a 40° angle like our Australian cousins.",
                            "children": [],
                        }
                    ],
                },
            ],
        },
        {
            "author": "BrownFeathers",
            "text": "Anyone spotted those &quot;silver fish&quot; near the rocks?",
            "children": [
                {
                    "author": "GulfGlider",
                    "text": "Yes! They're best caught at dawn.<p>Just remember: <code>swoop &gt; grab &gt; lift</code>",
                    "children": [],
                }
            ],
        },
    ],
}

def test_hacker_news_loader_with_uri(httpx_mock):
    httpx_mock.add_response(json=EXAMPLE)
    fragment = hacker_news_loader("https://news.ycombinator.com/item?id=123456")
    assert isinstance(fragment, llm.Fragment)
    assert fragment.source == "https://news.ycombinator.com/item?id=123456"
