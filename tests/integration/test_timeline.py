# Copyright (C) 2014 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014 Anler Hernández <hello@anler.me>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

from .. import factories

from taiga.projects.history import services as history_services
from taiga.timeline import service
from taiga.timeline.models import Timeline


pytestmark = pytest.mark.django_db


def test_add_to_object_timeline():
    Timeline.objects.all().delete()
    user1 = factories.UserFactory()
    user2 = factories.UserFactory()

    service.register_timeline_implementation("users.user", "test", lambda x, extra_data=None: str(id(x)))

    service._add_to_object_timeline(user1, user2, "test")

    assert Timeline.objects.filter(object_id=user1.id).count() == 1
    assert Timeline.objects.order_by("-id")[0].data == id(user2)


def test_get_timeline():
    Timeline.objects.all().delete()

    user1 = factories.UserFactory()
    user2 = factories.UserFactory()
    user3 = factories.UserFactory()
    user4 = factories.UserFactory()

    service.register_timeline_implementation("users.user", "test", lambda x, extra_data=None: str(id(x)))

    service._add_to_object_timeline(user1, user1, "test")
    service._add_to_object_timeline(user1, user2, "test")
    service._add_to_object_timeline(user1, user3, "test")
    service._add_to_object_timeline(user1, user4, "test")

    service._add_to_object_timeline(user2, user1, "test")

    assert service.get_timeline(user1).count() == 4
    assert service.get_timeline(user2).count() == 1
    assert service.get_timeline(user3).count() == 0


def test_create_project_timeline():
    project = factories.ProjectFactory.create(name="test project timeline")
    history_services.take_snapshot(project, user=project.owner)
    project_timeline = service.get_timeline(project).order_by("-created")
    assert project_timeline[0].event_type == "projects.project.create"
    assert project_timeline[0].data["project"]["name"] == "test project timeline"
    assert project_timeline[0].data["user"]["pk"] == project.owner.id
    assert project_timeline[0].data["user"]["name"] == project.owner.get_full_name()


def test_create_milestone_timeline():
    milestone = factories.MilestoneFactory.create(name="test milestone timeline")
    history_services.take_snapshot(milestone, user=milestone.owner)
    milestone_timeline = service.get_timeline(milestone.project).order_by("-created")
    assert milestone_timeline[0].event_type == "milestones.milestone.create"
    assert milestone_timeline[0].data["milestone"]["name"] == "test milestone timeline"
    assert milestone_timeline[0].data["user"]["pk"] == milestone.owner.id
    assert milestone_timeline[0].data["user"]["name"] == milestone.owner.get_full_name()


def test_create_user_story_timeline():
    user_story = factories.UserStoryFactory.create(subject="test us timeline")
    history_services.take_snapshot(user_story, user=user_story.owner)
    project_timeline = service.get_timeline(user_story.project).order_by("-created")
    assert project_timeline[0].event_type == "userstories.userstory.create"
    assert project_timeline[0].data["userstory"]["subject"] == "test us timeline"
    assert project_timeline[0].data["user"]["pk"] == user_story.owner.id
    assert project_timeline[0].data["user"]["name"] == user_story.owner.get_full_name()


def test_create_issue_timeline():
    issue = factories.IssueFactory.create(subject="test issue timeline")
    history_services.take_snapshot(issue, user=issue.owner)
    project_timeline = service.get_timeline(issue.project).order_by("-created")
    assert project_timeline[0].event_type == "issues.issue.create"
    assert project_timeline[0].data["issue"]["subject"] == "test issue timeline"
    assert project_timeline[0].data["user"]["pk"] == issue.owner.id
    assert project_timeline[0].data["user"]["name"] == issue.owner.get_full_name()


def test_create_task_timeline():
    task = factories.TaskFactory.create(subject="test task timeline")
    history_services.take_snapshot(task, user=task.owner)
    project_timeline = service.get_timeline(task.project).order_by("-created")
    assert project_timeline[0].event_type == "tasks.task.create"
    assert project_timeline[0].data["task"]["subject"] == "test task timeline"
    assert project_timeline[0].data["user"]["pk"] == task.owner.id
    assert project_timeline[0].data["user"]["name"] == task.owner.get_full_name()


def test_create_wiki_page_timeline():
    page = factories.WikiPageFactory.create(slug="test wiki page timeline")
    history_services.take_snapshot(page, user=page.owner)
    project_timeline = service.get_timeline(page.project).order_by("-created")
    assert project_timeline[0].event_type == "wiki.wikipage.create"
    assert project_timeline[0].data["wiki_page"]["slug"] == "test wiki page timeline"
    assert project_timeline[0].data["user"]["pk"] == page.owner.id
    assert project_timeline[0].data["user"]["name"] == page.owner.get_full_name()


def test_update_project_timeline():
    project = factories.ProjectFactory.create(name="test project timeline")
    history_services.take_snapshot(project, user=project.owner)
    project.name = "test project timeline updated"
    project.save()
    history_services.take_snapshot(project, user=project.owner)
    project_timeline = service.get_timeline(project).order_by("-created")
    assert project_timeline[0].event_type == "projects.project.change"
    assert project_timeline[0].data["project"]["name"] == "test project timeline updated"
    assert project_timeline[0].data["values_diff"]["name"][0] == "test project timeline"
    assert project_timeline[0].data["values_diff"]["name"][1] == "test project timeline updated"


def test_update_milestone_timeline():
    milestone = factories.MilestoneFactory.create(name="test milestone timeline")
    history_services.take_snapshot(milestone, user=milestone.owner)
    milestone.name = "test milestone timeline updated"
    milestone.save()
    history_services.take_snapshot(milestone, user=milestone.owner)
    project_timeline = service.get_timeline(milestone.project).order_by("-created")
    assert project_timeline[0].event_type == "milestones.milestone.change"
    assert project_timeline[0].data["milestone"]["name"] == "test milestone timeline updated"
    assert project_timeline[0].data["values_diff"]["name"][0] == "test milestone timeline"
    assert project_timeline[0].data["values_diff"]["name"][1] == "test milestone timeline updated"


def test_update_user_story_timeline():
    user_story = factories.UserStoryFactory.create(subject="test us timeline")
    history_services.take_snapshot(user_story, user=user_story.owner)
    user_story.subject = "test us timeline updated"
    user_story.save()
    history_services.take_snapshot(user_story, user=user_story.owner)
    project_timeline = service.get_timeline(user_story.project).order_by("-created")
    assert project_timeline[0].event_type == "userstories.userstory.change"
    assert project_timeline[0].data["userstory"]["subject"] == "test us timeline updated"
    assert project_timeline[0].data["values_diff"]["subject"][0] == "test us timeline"
    assert project_timeline[0].data["values_diff"]["subject"][1] == "test us timeline updated"


def test_update_issue_timeline():
    issue = factories.IssueFactory.create(subject="test issue timeline")
    history_services.take_snapshot(issue, user=issue.owner)
    issue.subject = "test issue timeline updated"
    issue.save()
    history_services.take_snapshot(issue, user=issue.owner)
    project_timeline = service.get_timeline(issue.project).order_by("-created")
    assert project_timeline[0].event_type == "issues.issue.change"
    assert project_timeline[0].data["issue"]["subject"] == "test issue timeline updated"
    assert project_timeline[0].data["values_diff"]["subject"][0] == "test issue timeline"
    assert project_timeline[0].data["values_diff"]["subject"][1] == "test issue timeline updated"


def test_update_task_timeline():
    task = factories.TaskFactory.create(subject="test task timeline")
    history_services.take_snapshot(task, user=task.owner)
    task.subject = "test task timeline updated"
    task.save()
    history_services.take_snapshot(task, user=task.owner)
    project_timeline = service.get_timeline(task.project).order_by("-created")
    assert project_timeline[0].event_type == "tasks.task.change"
    assert project_timeline[0].data["task"]["subject"] == "test task timeline updated"
    assert project_timeline[0].data["values_diff"]["subject"][0] == "test task timeline"
    assert project_timeline[0].data["values_diff"]["subject"][1] == "test task timeline updated"


def test_update_wiki_page_timeline():
    page = factories.WikiPageFactory.create(slug="test wiki page timeline")
    history_services.take_snapshot(page, user=page.owner)
    page.slug = "test wiki page timeline updated"
    page.save()
    history_services.take_snapshot(page, user=page.owner)
    project_timeline = service.get_timeline(page.project).order_by("-created")
    assert project_timeline[0].event_type == "wiki.wikipage.change"
    assert project_timeline[0].data["wiki_page"]["slug"] == "test wiki page timeline updated"
    assert project_timeline[0].data["values_diff"]["slug"][0] == "test wiki page timeline"
    assert project_timeline[0].data["values_diff"]["slug"][1] == "test wiki page timeline updated"


def test_delete_project_timeline():
    project = factories.ProjectFactory.create(name="test project timeline")
    #TODO


def test_delete_milestone_timeline():
    milestone = factories.MilestoneFactory.create(name="test milestone timeline")
    history_services.take_snapshot(milestone, user=milestone.owner, delete=True)
    project_timeline = service.get_timeline(milestone.project).order_by("-created")
    assert project_timeline[0].event_type == "milestones.milestone.delete"
    assert project_timeline[0].data["milestone"]["name"] == "test milestone timeline"


def test_delete_user_story_timeline():
    user_story = factories.UserStoryFactory.create(subject="test us timeline")
    history_services.take_snapshot(user_story, user=user_story.owner, delete=True)
    project_timeline = service.get_timeline(user_story.project).order_by("-created")
    assert project_timeline[0].event_type == "userstories.userstory.delete"
    assert project_timeline[0].data["userstory"]["subject"] == "test us timeline"


def test_delete_issue_timeline():
    issue = factories.IssueFactory.create(subject="test issue timeline")
    history_services.take_snapshot(issue, user=issue.owner, delete=True)
    project_timeline = service.get_timeline(issue.project).order_by("-created")
    assert project_timeline[0].event_type == "issues.issue.delete"
    assert project_timeline[0].data["issue"]["subject"] == "test issue timeline"


def test_delete_task_timeline():
    task = factories.TaskFactory.create(subject="test task timeline")
    history_services.take_snapshot(task, user=task.owner, delete=True)
    project_timeline = service.get_timeline(task.project).order_by("-created")
    assert project_timeline[0].event_type == "tasks.task.delete"
    assert project_timeline[0].data["task"]["subject"] == "test task timeline"


def test_delete_wiki_page_timeline():
    page = factories.WikiPageFactory.create(slug="test wiki page timeline")
    history_services.take_snapshot(page, user=page.owner, delete=True)
    project_timeline = service.get_timeline(page.project).order_by("-created")
    assert project_timeline[0].event_type == "wiki.wikipage.delete"
    assert project_timeline[0].data["wiki_page"]["slug"] == "test wiki page timeline"
