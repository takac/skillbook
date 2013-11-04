import logging
from django.test import TestCase
from django.utils import timezone
from skillbook.models import Resource, Skill
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class SkillTestCase(TestCase):
    def setUp(self):
        time = timezone.now()
        Skill.objects.create(name="blank",
                description="here description",
                user=User.objects.get(id=1),
                last_updated_user=User.objects.get(id=1),
                creation_date=time,
                update_date=time)
    def test_skill_name(self):
        pass
        # self.assertEqual("hello", "world")

private_urls = [
    '/skills/create/',
    '/account/profile/',
    '/account/activity/',
    ]

public_only_urls = [
        '/account/create/',
    ]

public_urls = [
        '/',
        '/skills/',
        '/skills/json/',
        '/skills/search/',
        '/resources/',
        '/users/',
        '/account/login/',
        '/account/create/',
        ]

# TODO force redirect from /accounts/login/ when already logged in

class SkillbookViewsTestCase(TestCase):

    def url_check(self, url, status):
        logger.info("Checking for %d status from: %s" % (status, url))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status, 'not %d status from %s, got %d' % (status, url, resp.status_code))

    def test_public_urls(self):
        for i in public_urls:
            self.url_check(i, 200)
    
    def test_public_only_urls(self):
        self.client.login(username='tomc', password='djangotest')
        for i in public_only_urls:
            self.url_check(i, 302)

    def test_private_urls_without_login(self):
        self.client.login(username='tomc', password='notpassw')
        for i in private_urls:
            self.url_check(i, 302)

    def test_private_urls_with_login(self):
        self.client.login(username='tomc', password='djangotest')
        for i in private_urls:
            self.url_check(i, 200)



