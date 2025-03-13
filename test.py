import protego


def test_protego_behavior():
    print("Testing Protego robots.txt parsing behavior")

    # Test standard robots.txt content
    robots_txt = """User-agent: *
Disallow: /private/
Allow: /public/

User-agent: test-bot
Disallow: /test-private/

Sitemap: https://example.com/sitemap.xml
"""

    parser = protego.Protego.parse(robots_txt)

    # Test URLs with default user-agent
    print("\nDefault user-agent:")
    print(f"Can fetch /public/page: {parser.can_fetch('/public/page', '*')}")
    print(f"Can fetch /private/page: {parser.can_fetch('/private/page', '*')}")
    print(
        f"Can fetch /test-private/page: {parser.can_fetch('/test-private/page', '*')}"
    )
    print(f"Can fetch /other/page: {parser.can_fetch('/other/page', '*')}")

    # Test URLs with specific user-agent
    print("\ntest-bot user-agent:")
    print(f"Can fetch /public/page: {parser.can_fetch('/public/page', 'test-bot')}")
    print(f"Can fetch /private/page: {parser.can_fetch('/private/page', 'test-bot')}")
    print(
        f"Can fetch /test-private/page: {parser.can_fetch('/test-private/page', 'test-bot')}"
    )
    print(f"Can fetch /other/page: {parser.can_fetch('/other/page', 'test-bot')}")

    # Test with different URL formats
    print("\nTesting different URL formats:")
    print(f"Path only: {parser.can_fetch('/private/page', '*')}")
    print(f"Full URL: {parser.can_fetch('https://example.com/private/page', '*')}")
    print(
        f"URL with query: {parser.can_fetch('https://example.com/private/page?q=test', '*')}"
    )

    # Extract sitemaps
    print("\nSitemaps:")
    sitemaps = parser.sitemaps
    for sitemap in sitemaps:
        print(f"- {sitemap}")

    # Test different spacing in robots.txt
    print("\nTesting with indented content:")
    indented_robots_txt = """    User-agent: *
    Disallow: /private/
    Allow: /public/
"""
    try:
        indented_parser = protego.Protego.parse(indented_robots_txt)
        print(
            f"Can fetch /private/page: {indented_parser.can_fetch('/private/page', '*')}"
        )
    except Exception as e:
        print(f"Error parsing indented content: {e}")


if __name__ == "__main__":
    test_protego_behavior()

"""
(venv) ➜  ethicrawl git:(develop) ✗ python test.py
Testing Protego robots.txt parsing behavior

Default user-agent:
Can fetch /public/page: True
Can fetch /private/page: False
Can fetch /test-private/page: True
Can fetch /other/page: True

test-bot user-agent:
Can fetch /public/page: True
Can fetch /private/page: True
Can fetch /test-private/page: False
Can fetch /other/page: True

Testing different URL formats:
Path only: False
Full URL: False
URL with query: False

Sitemaps:
- https://example.com/sitemap.xml

Testing with indented content:
Can fetch /private/page: False
"""
