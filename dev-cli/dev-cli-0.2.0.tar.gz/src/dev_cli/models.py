from dataclasses import dataclass
from typing import List, Optional, Text, Union

from typefit import narrows


@dataclass(frozen=True)
class User:
    name: Text
    username: Text
    twitter_username: Optional[Text] = None
    github_username: Optional[Text] = None
    website_url: Optional[Text] = None
    profile_image: Optional[Text] = None
    profile_image_90: Optional[Text] = None


@dataclass(frozen=True)
class Organization:
    name: Text
    username: Text
    slug: Text
    profile_image: Optional[Text]
    profile_image_90: Optional[Text]


@dataclass(frozen=True)
class FlareTag:
    name: Text
    bg_color_hex: Text
    text_color_hex: Text


@dataclass(frozen=True)
class ListArticle:
    type_of: Text
    id: int
    title: Text
    description: Text
    readable_publish_date: Text
    social_image: Text
    tag_list: List[Text]
    tags: Text
    slug: Text
    path: Text
    url: Text
    canonical_url: Text
    comments_count: int
    positive_reactions_count: int
    created_at: narrows.DateTime
    user: User
    collection_id: Optional[int] = None
    cover_image: Optional[Text] = None
    crossposted_at: Optional[narrows.DateTime] = None
    edited_at: Optional[narrows.DateTime] = None
    published_at: Optional[narrows.DateTime] = None
    last_comment_at: Optional[narrows.DateTime] = None
    published_timestamp: Optional[narrows.DateTime] = None
    organization: Optional[Organization] = None
    flare_tag: Optional[FlareTag] = None


@dataclass(frozen=True)
class MeArticle:
    type_of: Text
    id: int
    title: Text
    description: Text
    tag_list: List[Text]
    slug: Text
    path: Text
    url: Text
    canonical_url: Text
    comments_count: int
    positive_reactions_count: int
    published: bool
    body_markdown: Text
    user: User
    collection_id: Optional[int] = None
    cover_image: Optional[Text] = None
    crossposted_at: Optional[narrows.DateTime] = None
    edited_at: Optional[narrows.DateTime] = None
    published_at: Optional[narrows.DateTime] = None
    last_comment_at: Optional[narrows.DateTime] = None
    published_timestamp: Union[None, Text, narrows.DateTime] = None
    organization: Optional[Organization] = None
    flare_tag: Optional[FlareTag] = None


@dataclass(frozen=True)
class WriteArticle:
    type_of: Text
    id: int
    title: Text
    description: Text
    tags: List[Text]
    tag_list: Text
    slug: Text
    path: Text
    url: Text
    canonical_url: Text
    comments_count: int
    positive_reactions_count: int
    body_html: Text
    body_markdown: Text
    user: User
    collection_id: Optional[int] = None
    cover_image: Optional[Text] = None
    crossposted_at: Optional[narrows.DateTime] = None
    edited_at: Optional[narrows.DateTime] = None
    published_at: Optional[narrows.DateTime] = None
    last_comment_at: Optional[narrows.DateTime] = None
    published_timestamp: Union[None, Text, narrows.DateTime] = None
    organization: Optional[Organization] = None
    flare_tag: Optional[FlareTag] = None


@dataclass(frozen=True)
class SingleArticle:
    type_of: Text
    id: int
    title: Text
    description: Text
    readable_publish_date: Text
    social_image: Text
    tags: List[Text]
    tag_list: Text
    slug: Text
    path: Text
    url: Text
    canonical_url: Text
    comments_count: int
    positive_reactions_count: int
    created_at: narrows.DateTime
    body_html: Text
    body_markdown: Text
    user: User
    collection_id: Optional[int] = None
    cover_image: Optional[Text] = None
    crossposted_at: Optional[narrows.DateTime] = None
    edited_at: Optional[narrows.DateTime] = None
    published_at: Optional[narrows.DateTime] = None
    last_comment_at: Optional[narrows.DateTime] = None
    published_timestamp: Optional[narrows.DateTime] = None
    organization: Optional[Organization] = None
    flare_tag: Optional[FlareTag] = None
