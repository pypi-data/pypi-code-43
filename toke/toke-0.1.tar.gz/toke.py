#!/usr/bin/env python3

import click
from dotenv import load_dotenv
import os
import tweepy


load_dotenv()
PASSWORD = os.getenv("PASSWORD")

OPEN_TEMPLETE = 'docker run -dt --name ss{port} -p {port}:{port} mritd/shadowsocks -s "-s 0.0.0.0 -p {port} -m aes-256-cfb -k {password} --fast-open"'
CLOSE_TEMPLETE = "docker rm -f ss{port}"
consumer_key = os.getenv("consumerKey")
consumer_secret = os.getenv("consumerSecret")
access_token = os.getenv("accessToken")
access_token_secret = os.getenv("accessSecret")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo("Hello %s!" % name)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--f", default=1500, help="Number of start port.")
@click.option("--t", default=1520, help="Number of end port.")
def open(f, t):
    for p in range(f, t + 1):
        # click.echo(p)
        click.echo(OPEN_TEMPLETE.format(port=p, password=PASSWORD))


@cli.command()
@click.option("--f", default=1500, help="Number of start port.")
@click.option("--t", default=1520, help="Number of end port.")
def close(f, t):
    for p in range(f, t + 1):
        # click.echo(p)
        # click.echo(OPEN_TEMPLETE.format(port=p, password=PASSWORD))
        click.echo(CLOSE_TEMPLETE.format(port=p))


@cli.command()
@click.argument("count")
def home(count):
    public_tweets = api.user_timeline(count=int(count))
    for num, tweet in enumerate(public_tweets, start=0):
        if num > 0:
            print(num, ": ", tweet.text)


@cli.command()
@click.argument('status')
def post(status):
    api.update_status(status)


@cli.command()
@click.argument("count")
def delete(count):
    tweets = api.user_timeline(count=int(count))
    for num, tweet in enumerate(tweets, start=0):
        if num > 0:
            print(num, ": ", tweet.text)
            api.destroy_status(tweets[num].id)



cli.add_command(open)
cli.add_command(close)
cli.add_command(hello)
cli.add_command(home)
cli.add_command(post)
cli.add_command(delete)

if __name__ == "__main__":
    cli()
