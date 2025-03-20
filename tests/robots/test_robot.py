import pytest
from unittest.mock import Mock

<<<<<<< HEAD
from ethicrawl.robots import Robot, RobotFactory
from ethicrawl.robots.robotochan import RobotoChan
from ethicrawl.context import Context
from ethicrawl.error import RobotDisallowedError
=======
from ethicrawl.robots import Robot, RobotFactory, RobotDisallowedError

from ethicrawl.robots.robotochan import RobotoChan
from ethicrawl.context import Context
>>>>>>> main
from ethicrawl.core import Url, Resource
from ethicrawl.client import Client


empty_robots_txt = """
"""

robots_txt = """
# version: 49987aec3c503f82fc2e72d0413322dea656d6da

# HTTPS www.example.com

User-agent: *
Sitemap: https://www.example.com/sitemap.xml

Disallow: /search$
Disallow: /search/
Disallow: /search?

User-agent: foo-bar-baz
Disallow: /
"""


class TestRobot:
    def test_new_robot(self):
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))
        assert isinstance(Robot(RobotFactory.robotify(Url(url)), context), Robot)
        assert isinstance(RobotoChan(RobotFactory.robotify(Url(url)), context), Robot)

    def test_robot_init_200_status(self):
        """Test Robot initialization with 200 status code."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = robots_txt
        mock_client.get.return_value = mock_response

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # Test the parser was initialized with the robots.txt content
        assert robot._parser is not None
        # Verify get was called with robots.txt URL
        mock_client.get.assert_called_once()

    def test_robot_init_404_status(self):
        """Test Robot initialization with 404 status (fail open)."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = robots_txt
        mock_client.get.return_value = mock_response

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # Test the parser was initialized with the robots.txt content
        assert robot._parser is not None
        # Verify get was called with robots.txt URL
        mock_client.get.assert_called_once()

    def test_robot_init_error_status(self):
        """Test Robot initialization with error status (fail closed)."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = robots_txt
        mock_client.get.return_value = mock_response

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # Test the parser was initialized with the robots.txt content
        assert robot._parser is not None
        # Verify get was called with robots.txt URL
        mock_client.get.assert_called_once()

    def test_can_fetch_allowed(self):
        """Test allowed URL paths."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = robots_txt
        mock_client.get.return_value = mock_response
        mock_client.user_agent = "test-agent"

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # These paths should be allowed based on robots.txt
        assert robot.can_fetch("https://www.example.com/about") is True
        assert robot.can_fetch("https://www.example.com/products") is True
        assert robot.can_fetch("https://www.example.com/") is True

    def test_can_fetch_disallowed(self):
        """Test disallowed URL paths."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = robots_txt
        mock_client.get.return_value = mock_response
        mock_client.user_agent = "test-agent"

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # These paths should be disallowed based on robots.txt
        with pytest.raises(RobotDisallowedError):
            robot.can_fetch("https://www.example.com/search")

        with pytest.raises(RobotDisallowedError):
            robot.can_fetch("https://www.example.com/search/")

        with pytest.raises(RobotDisallowedError):
            robot.can_fetch("https://www.example.com/search?q=test")

    def test_can_fetch_input_types(self):
        """Test different input types to can_fetch."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 200
        # Use empty robots.txt for simplicity (allows everything)
        mock_response.text = empty_robots_txt
        mock_client.get.return_value = mock_response
        mock_client.user_agent = "test-agent"

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        test_url = "https://www.example.com/page"

        # Test string URL
        assert robot.can_fetch(test_url) is True

        # Test Url object
        assert robot.can_fetch(Url(test_url)) is True

        # Test Resource object
        assert robot.can_fetch(Resource(test_url)) is True

        # Test invalid type
        with pytest.raises(TypeError):
            robot.can_fetch(123)

    def test_can_fetch_specific_user_agent(self):
        """Test robots.txt rules specific to certain user agents."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = robots_txt
        mock_client.get.return_value = mock_response

        # First with default agent
        mock_client.user_agent = "test-agent"
        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # Should be allowed for default agent
        assert robot.can_fetch("https://www.example.com/about") is True

        # Now with the restricted agent
        mock_client.user_agent = "foo-bar-baz"
        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # Should be disallowed for foo-bar-baz agent
        with pytest.raises(RobotDisallowedError):
            robot.can_fetch("https://www.example.com/about")

        with pytest.raises(RobotDisallowedError):
            robot.can_fetch("https://www.example.com/")

        with pytest.raises(RobotDisallowedError):
            robot.can_fetch("https://www.example.com/anything")

    def test_sitemaps_property(self):
        """Test sitemap extraction from robots.txt."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = robots_txt  # Contains Sitemap entry
        mock_client.get.return_value = mock_response

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # Get sitemaps from the robot
        sitemaps = robot.sitemaps

        # Verify it's a ResourceList
        assert len(sitemaps) == 1

        # Verify the sitemap URL is correct
        assert str(sitemaps[0].url) == "https://www.example.com/sitemap.xml"

    def test_sitemaps_property_empty(self):
        """Test sitemap extraction when none exist."""
        url = "https://www.example.com"
        mock_client = Mock(spec=Client)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = empty_robots_txt  # No Sitemap entries
        mock_client.get.return_value = mock_response

        context = Context(Resource(url), mock_client)
        robot = Robot(RobotFactory.robotify(Url(url)), context)

        # Get sitemaps from the robot
        sitemaps = robot.sitemaps

        # Verify it's an empty ResourceList
        assert len(sitemaps) == 0

    def test_context(self):
        url = "https://www.example.com"
        context = Context(Resource(Url(url)))
        assert Robot(RobotFactory.robotify(Url(url)), context).context == context
