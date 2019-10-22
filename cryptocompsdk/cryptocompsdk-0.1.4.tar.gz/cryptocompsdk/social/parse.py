from copy import deepcopy
from typing import Optional, Any, List

import pandas as pd

from cryptocompsdk.general.parse import from_int, from_none, from_union, from_float, from_str, to_float, from_bool, \
    from_list, to_class, from_plain_dict
from cryptocompsdk.response import ResponseException, ResponseAPIBase


class SocialRecord:
    time: Optional[int]
    comments: Optional[int]
    posts: Optional[int]
    followers: Optional[int]
    points: Optional[int]
    overview_page_views: Optional[int]
    analysis_page_views: Optional[int]
    markets_page_views: Optional[int]
    charts_page_views: Optional[int]
    trades_page_views: Optional[int]
    forum_page_views: Optional[int]
    influence_page_views: Optional[int]
    total_page_views: Optional[int]
    fb_likes: Optional[int]
    fb_talking_about: Optional[int]
    twitter_followers: Optional[int]
    twitter_following: Optional[int]
    twitter_lists: Optional[int]
    twitter_favourites: Optional[int]
    twitter_statuses: Optional[int]
    reddit_subscribers: Optional[int]
    reddit_active_users: Optional[int]
    reddit_posts_per_hour: Optional[float]
    reddit_posts_per_day: Optional[float]
    reddit_comments_per_hour: Optional[float]
    reddit_comments_per_day: Optional[float]
    code_repo_stars: Optional[int]
    code_repo_forks: Optional[int]
    code_repo_subscribers: Optional[int]
    code_repo_open_pull_issues: Optional[int]
    code_repo_closed_pull_issues: Optional[int]
    code_repo_open_issues: Optional[int]
    code_repo_closed_issues: Optional[int]
    code_repo_contributors: Optional[int]

    def __init__(self, time: Optional[int], comments: Optional[int], posts: Optional[int], followers: Optional[int],
                 points: Optional[int], overview_page_views: Optional[int], analysis_page_views: Optional[int],
                 markets_page_views: Optional[int], charts_page_views: Optional[int], trades_page_views: Optional[int],
                 forum_page_views: Optional[int], influence_page_views: Optional[int], total_page_views: Optional[int],
                 fb_likes: Optional[int], fb_talking_about: Optional[int], twitter_followers: Optional[int],
                 twitter_following: Optional[int], twitter_lists: Optional[int], twitter_favourites: Optional[int],
                 twitter_statuses: Optional[int], reddit_subscribers: Optional[int], reddit_active_users: Optional[int],
                 reddit_posts_per_hour: Optional[float], reddit_posts_per_day: Optional[float],
                 reddit_comments_per_hour: Optional[float], reddit_comments_per_day: Optional[float],
                 code_repo_stars: Optional[int], code_repo_forks: Optional[int], code_repo_subscribers: Optional[int],
                 code_repo_open_pull_issues: Optional[int], code_repo_closed_pull_issues: Optional[int],
                 code_repo_open_issues: Optional[int], code_repo_closed_issues: Optional[int],
                 code_repo_contributors: Optional[int]) -> None:
        self.time = time
        self.comments = comments
        self.posts = posts
        self.followers = followers
        self.points = points
        self.overview_page_views = overview_page_views
        self.analysis_page_views = analysis_page_views
        self.markets_page_views = markets_page_views
        self.charts_page_views = charts_page_views
        self.trades_page_views = trades_page_views
        self.forum_page_views = forum_page_views
        self.influence_page_views = influence_page_views
        self.total_page_views = total_page_views
        self.fb_likes = fb_likes
        self.fb_talking_about = fb_talking_about
        self.twitter_followers = twitter_followers
        self.twitter_following = twitter_following
        self.twitter_lists = twitter_lists
        self.twitter_favourites = twitter_favourites
        self.twitter_statuses = twitter_statuses
        self.reddit_subscribers = reddit_subscribers
        self.reddit_active_users = reddit_active_users
        self.reddit_posts_per_hour = reddit_posts_per_hour
        self.reddit_posts_per_day = reddit_posts_per_day
        self.reddit_comments_per_hour = reddit_comments_per_hour
        self.reddit_comments_per_day = reddit_comments_per_day
        self.code_repo_stars = code_repo_stars
        self.code_repo_forks = code_repo_forks
        self.code_repo_subscribers = code_repo_subscribers
        self.code_repo_open_pull_issues = code_repo_open_pull_issues
        self.code_repo_closed_pull_issues = code_repo_closed_pull_issues
        self.code_repo_open_issues = code_repo_open_issues
        self.code_repo_closed_issues = code_repo_closed_issues
        self.code_repo_contributors = code_repo_contributors

    @staticmethod
    def from_dict(obj: Any) -> 'SocialRecord':
        assert isinstance(obj, dict)
        time = from_union([from_int, from_none], obj.get("time"))
        comments = from_union([from_int, from_none], obj.get("comments"))
        posts = from_union([from_int, from_none], obj.get("posts"))
        followers = from_union([from_int, from_none], obj.get("followers"))
        points = from_union([from_int, from_none], obj.get("points"))
        overview_page_views = from_union([from_int, from_none], obj.get("overview_page_views"))
        analysis_page_views = from_union([from_int, from_none], obj.get("analysis_page_views"))
        markets_page_views = from_union([from_int, from_none], obj.get("markets_page_views"))
        charts_page_views = from_union([from_int, from_none], obj.get("charts_page_views"))
        trades_page_views = from_union([from_int, from_none], obj.get("trades_page_views"))
        forum_page_views = from_union([from_int, from_none], obj.get("forum_page_views"))
        influence_page_views = from_union([from_int, from_none], obj.get("influence_page_views"))
        total_page_views = from_union([from_int, from_none], obj.get("total_page_views"))
        fb_likes = from_union([from_int, from_none], obj.get("fb_likes"))
        fb_talking_about = from_union([from_int, from_none], obj.get("fb_talking_about"))
        twitter_followers = from_union([from_int, from_none], obj.get("twitter_followers"))
        twitter_following = from_union([from_int, from_none], obj.get("twitter_following"))
        twitter_lists = from_union([from_int, from_none], obj.get("twitter_lists"))
        twitter_favourites = from_union([from_int, from_none], obj.get("twitter_favourites"))
        twitter_statuses = from_union([from_int, from_none], obj.get("twitter_statuses"))
        reddit_subscribers = from_union([from_int, from_none], obj.get("reddit_subscribers"))
        reddit_active_users = from_union([from_int, from_none], obj.get("reddit_active_users"))
        reddit_posts_per_hour = from_union([from_float, from_none], obj.get("reddit_posts_per_hour"))
        reddit_posts_per_day = from_union([from_float, from_none], obj.get("reddit_posts_per_day"))
        reddit_comments_per_hour = from_union([from_float, from_none], obj.get("reddit_comments_per_hour"))
        reddit_comments_per_day = from_union([from_float, from_none], obj.get("reddit_comments_per_day"))
        code_repo_stars = from_union([from_int, from_none], obj.get("code_repo_stars"))
        code_repo_forks = from_union([from_int, from_none], obj.get("code_repo_forks"))
        code_repo_subscribers = from_union([from_int, from_none], obj.get("code_repo_subscribers"))
        code_repo_open_pull_issues = from_union([from_int, from_none], obj.get("code_repo_open_pull_issues"))
        code_repo_closed_pull_issues = from_union([from_int, from_none], obj.get("code_repo_closed_pull_issues"))
        code_repo_open_issues = from_union([from_int, from_none], obj.get("code_repo_open_issues"))
        code_repo_closed_issues = from_union([from_int, from_none], obj.get("code_repo_closed_issues"))
        code_repo_contributors = from_union([from_int, from_none], obj.get("code_repo_contributors"))
        return SocialRecord(time, comments, posts, followers, points, overview_page_views, analysis_page_views,
                            markets_page_views, charts_page_views, trades_page_views, forum_page_views,
                            influence_page_views, total_page_views, fb_likes, fb_talking_about, twitter_followers,
                            twitter_following, twitter_lists, twitter_favourites, twitter_statuses, reddit_subscribers,
                            reddit_active_users, reddit_posts_per_hour, reddit_posts_per_day, reddit_comments_per_hour,
                            reddit_comments_per_day, code_repo_stars, code_repo_forks, code_repo_subscribers,
                            code_repo_open_pull_issues, code_repo_closed_pull_issues, code_repo_open_issues,
                            code_repo_closed_issues, code_repo_contributors)

    def to_dict(self) -> dict:
        result: dict = {}
        result["time"] = from_union([from_int, from_none], self.time)
        result["comments"] = from_union([from_int, from_none], self.comments)
        result["posts"] = from_union([from_int, from_none], self.posts)
        result["followers"] = from_union([from_int, from_none], self.followers)
        result["points"] = from_union([from_int, from_none], self.points)
        result["overview_page_views"] = from_union([from_int, from_none], self.overview_page_views)
        result["analysis_page_views"] = from_union([from_int, from_none], self.analysis_page_views)
        result["markets_page_views"] = from_union([from_int, from_none], self.markets_page_views)
        result["charts_page_views"] = from_union([from_int, from_none], self.charts_page_views)
        result["trades_page_views"] = from_union([from_int, from_none], self.trades_page_views)
        result["forum_page_views"] = from_union([from_int, from_none], self.forum_page_views)
        result["influence_page_views"] = from_union([from_int, from_none], self.influence_page_views)
        result["total_page_views"] = from_union([from_int, from_none], self.total_page_views)
        result["fb_likes"] = from_union([from_int, from_none], self.fb_likes)
        result["fb_talking_about"] = from_union([from_int, from_none], self.fb_talking_about)
        result["twitter_followers"] = from_union([from_int, from_none], self.twitter_followers)
        result["twitter_following"] = from_union([from_int, from_none], self.twitter_following)
        result["twitter_lists"] = from_union([from_int, from_none], self.twitter_lists)
        result["twitter_favourites"] = from_union([from_int, from_none], self.twitter_favourites)
        result["twitter_statuses"] = from_union([from_int, from_none], self.twitter_statuses)
        result["reddit_subscribers"] = from_union([from_int, from_none], self.reddit_subscribers)
        result["reddit_active_users"] = from_union([from_int, from_none], self.reddit_active_users)
        result["reddit_posts_per_hour"] = from_union([to_float, from_none], self.reddit_posts_per_hour)
        result["reddit_posts_per_day"] = from_union([to_float, from_none], self.reddit_posts_per_day)
        result["reddit_comments_per_hour"] = from_union([to_float, from_none], self.reddit_comments_per_hour)
        result["reddit_comments_per_day"] = from_union([to_float, from_none], self.reddit_comments_per_day)
        result["code_repo_stars"] = from_union([from_int, from_none], self.code_repo_stars)
        result["code_repo_forks"] = from_union([from_int, from_none], self.code_repo_forks)
        result["code_repo_subscribers"] = from_union([from_int, from_none], self.code_repo_subscribers)
        result["code_repo_open_pull_issues"] = from_union([from_int, from_none], self.code_repo_open_pull_issues)
        result["code_repo_closed_pull_issues"] = from_union([from_int, from_none], self.code_repo_closed_pull_issues)
        result["code_repo_open_issues"] = from_union([from_int, from_none], self.code_repo_open_issues)
        result["code_repo_closed_issues"] = from_union([from_int, from_none], self.code_repo_closed_issues)
        result["code_repo_contributors"] = from_union([from_int, from_none], self.code_repo_contributors)
        return result

    @property
    def is_empty(self) -> bool:
        is_empty_cols = [
            'comments',
            'posts',
            'followers',
            'points',
            'overview_page_views',
            'analysis_page_views',
            'markets_page_views',
            'charts_page_views',
            'trades_page_views',
            'forum_page_views',
            'influence_page_views',
            'total_page_views',
            'fb_likes',
            'fb_talking_about',
            'twitter_followers',
            'twitter_following',
            'twitter_lists',
            'twitter_favourites',
            'twitter_statuses',
            'reddit_subscribers',
            'reddit_active_users',
            'reddit_posts_per_hour',
            'reddit_posts_per_day',
            'reddit_comments_per_hour',
            'reddit_comments_per_day',
            'code_repo_stars',
            'code_repo_forks',
            'code_repo_subscribers',
            'code_repo_open_pull_issues',
            'code_repo_closed_pull_issues',
            'code_repo_open_issues',
            'code_repo_closed_issues',
            'code_repo_contributors'
        ]

        for col in is_empty_cols:
            if getattr(self, col) != 0:
                return False
        return True


class RateLimit:
    pass

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> 'RateLimit':
        assert isinstance(obj, dict)
        return RateLimit()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


class SocialData(ResponseAPIBase):
    response: Optional[str]
    message: Optional[str]
    has_warning: Optional[bool]
    param_with_error: Optional[str]
    type: Optional[int]
    rate_limit: Optional[RateLimit]
    data: Optional[List[SocialRecord]]

    def __init__(self, response: Optional[str], message: Optional[str], has_warning: Optional[bool],
                 param_with_error: Optional[str], type: Optional[int], rate_limit: Optional[RateLimit],
                 data: Optional[List[SocialRecord]]) -> None:
        self.response = response
        self.message = message
        self.has_warning = has_warning
        self.param_with_error = param_with_error
        self.type = type
        self.rate_limit = rate_limit
        self.data = data

    @staticmethod
    def from_dict(obj: Any) -> 'SocialData':
        assert isinstance(obj, dict)
        response = from_union([from_str, from_none], obj.get("Response"))
        message = from_union([from_str, from_none], obj.get("Message"))
        has_warning = from_union([from_bool, from_none], obj.get("HasWarning"))
        param_with_error = from_union([from_str, from_none], obj.get("ParamWithError"))
        type = from_union([from_int, from_none], obj.get("Type"))
        rate_limit = from_union([RateLimit.from_dict, from_none], obj.get("RateLimit"))
        data = from_union([lambda x: from_list(SocialRecord.from_dict, x), from_none, from_plain_dict], obj.get("Data"))
        return SocialData(response, message, has_warning, param_with_error, type, rate_limit, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Response"] = from_union([from_str, from_none], self.response)
        result["Message"] = from_union([from_str, from_none], self.message)
        result["HasWarning"] = from_union([from_bool, from_none], self.has_warning)
        result["ParamWithError"] = from_union([from_str, from_none], self.param_with_error)
        result["Type"] = from_union([from_int, from_none], self.type)
        result["RateLimit"] = from_union([lambda x: to_class(RateLimit, x), from_none], self.rate_limit)
        result["Data"] = from_union([lambda x: from_list(lambda x: to_class(SocialRecord, x), x), from_none, from_plain_dict], self.data)
        return result

    def to_df(self) -> pd.DataFrame:
        if not self.data:
            return pd.DataFrame()
        df = pd.DataFrame(self.to_dict()['Data'])
        df['time'] = df['time'].apply(pd.Timestamp.fromtimestamp)
        return df

    # Pagination methods

    @property
    def is_empty(self) -> bool:
        for record in self.data:
            if not record.is_empty:
                return False

        return True

    def __add__(self, other):
        out_obj = deepcopy(self)
        out_obj.data += other.data
        return out_obj

    def __radd__(self, other):
        out_obj = deepcopy(other)
        out_obj.data += self.data
        return out_obj

    @property
    def time_from(self) -> int:
        times = [record.time for record in self.data]
        return min(times)

    def delete_record_matching_time(self, time: int):
        times = [record.time for record in self.data]
        try:
            idx = times.index(time)
        except ValueError:
            raise CouldNotGetSocialException(f'tried removing overlapping time {time} but was not in data')
        del self.data[idx]

    def trim_empty_records_at_beginning(self):
        self.data.reverse()  # now earliest records are at end

        # Delete, starting from end, oldest record
        for i, record in reversed(list(enumerate(self.data))):
            if record.is_empty:
                del self.data[i]
            else:
                # First non-empty record from end, we have now hit the actual data section, stop deleting
                break

        self.data.reverse()  # restore original order, earliest records at beginning


def social_data_from_dict(s: Any) -> SocialData:
    return SocialData.from_dict(s)


def social_data_to_dict(x: SocialData) -> Any:
    return to_class(SocialData, x)


class CouldNotGetSocialException(ResponseException):
    pass
