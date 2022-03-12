import re
from re import RegexFlag
from pathlib import Path
import os
import untangle
from markdownify import markdownify
from bs4 import BeautifulSoup

front_matter = """
---
title: "{}"
date: {}
draft: false
author: Ishan Sharma
"""

front_matter_end = "---"
gist_shortcode = "< gist {} {} >"
tweet_shortcode = "< tweet user=\"{}\" id=\"{}\" >"
yt_shortcode = "< youtube {} >"


def write_markdown_to(dirpath, name, content):
    # TODO: Check for md extension
    file_to_write = Path(dirpath + name + ".md")
    file_to_write.touch()
    file_to_write.write_text(content)


def create_or_empty_dir(dirpath):
    dir = Path(dirpath)
    if not dir.is_dir():
        dir.mkdir()
        return

    for f in dir.iterdir():
        os.remove(f)


def get_categories_and_tags(category_list):
    if not category_list:
        return ""

    if len(category_list) == 0:
        return ""

    out = ""
    categories = []
    tags = []

    # category will have attributes that define if it's a tag or category.
    # domain: 'post_tag'/'categoory'
    for c in category_list:
        if c['domain'] == 'post_tag':
            tags.append(c.cdata)
        if c['domain'] == 'category':
            categories.append(c.cdata)

    if len(categories) == 0 and len(tags) == 0:
        return out

    if len(categories) > 0:
        out += "categories:\n"

        for c in categories:
            out += "- " + c + "\n"

    if len(tags) > 0:
        out += "tags:\n"

        for t in tags:
            out += "- " + t + "\n"

    return out


def process_content(content):
    content = convert_gists(content)
    content = convert_tweets(content)
    content = convert_youtube(content)
    content = convert_images(content)

    return content


def convert_gists(content):
    # [embed]https://gist.github.com/ishansharma/11d4569830b6fc0322a1a7cc171e3c2b[/embed]
    # [gist]https://gist.github.com/ishansharma/f765bfede3199c285393382e4f42b2bd[/gist]
    p = re.compile(r'\[.{4,6}]https://gist.github.com/(.*)/(.*)\[/.{4,5}]')
    content = re.sub(p, replace_gist_shortcode, content)

    # https://gist.github.com/ishansharma/eb7f0fc05dc79312098952e319515095
    p2 = re.compile(r'https://gist.github.com/(.*)/(\w{32})')
    content = re.sub(p2, replace_gist_shortcode, content)

    return content


def replace_gist_shortcode(matchobj):
    if matchobj.group(1) and matchobj.group(2):
        return '{{' + gist_shortcode.format(matchobj.group(1), matchobj.group(2)) + '}}'

    return ' '


def convert_tweets(content):
    # https://twitter.com/allymacdonald/status/1024656834571976705
    p = re.compile(r'^https://twitter.com/(.+)/status/(\d+)$', flags=RegexFlag.MULTILINE)
    content = re.sub(p, replace_tweet_shortcode, content)

    return content


def convert_images(content):
    # Captions Shorttag
    #
    # Example caption
    # [caption id="attachment_129" align="aligncenter" width="566" caption="RBI, Sending Us One Step Backward!"]<img
    # class="size-full wp-image-129" title="PayPal Changes"
    # src="http://ishansharma.com/wp-content/uploads/2011/01/PayPal-Changes.png" alt="" width="566" height="456" />[
    # /caption]
    #
    # Output: {{< figure src="screen_time_maps.png#center" width=360 alt="Screenshot showing high Maps Usage" >}}
    p = re.compile(r'\[caption .+](.*)\[/caption]')
    # print(re.findall(p, content))
    content = re.sub(p, replace_caption_shorttag, content)
    content = replace_images_in_html(content)
    return content


def replace_caption_shorttag(matchobj):
    out = ' '
    if matchobj.group(1):
        soup = BeautifulSoup(matchobj.group(1), 'html.parser')
        image = soup.img
        out += get_image_shortcode(image)

    return out


def replace_images_in_html(content):
    soup = BeautifulSoup(content, 'html.parser')

    images = soup.findAll('img')
    if not len(images):
        return content

    for image in images:
        replacement = get_image_shortcode(image)
        if replacement:
            image.replace_with(replacement)

    content = str(soup)

    # Ugly hack to get Hugo shortcodes to work
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    return content


def get_image_shortcode(tag):
    out = '{{< figure src='

    source = tag.get('src')
    if not source:
        return ''
    source = source.replace('http://ishan.co', '')
    source = source.replace('http://ishansharma.com', '')
    out += '"{}#center"'.format(source)

    width = tag.get('width')
    if width:
        out += ' width={}'.format(width)

    height = tag.get('height')
    if height:
        out += ' height={}'.format(height)

    alt = tag.get('alt')
    if alt:
        alt = alt.replace('"', '\\"')
        out += ' alt="{}"'.format(alt)

    out += ' >}}'

    return out


def replace_tweet_shortcode(matchobj):
    if matchobj.group(1) and matchobj.group(2):
        return '{{' + tweet_shortcode.format(matchobj.group(1), matchobj.group(2)) + '}}'

    return ' '


def convert_youtube(content):
    # https://www.youtube.com/watch?v=T5Xx3MdqdgM
    # http://www.youtube.com/watch?v=nM_txL43iFM
    p = re.compile(r'http[s]{0,1}://www.youtube.com/watch\?v\=(.{11})')
    content = re.sub(p, replace_yt_shortcode, content)

    return content


def replace_yt_shortcode(matchobj):
    if matchobj.group(1):
        return '{{' + yt_shortcode.format(matchobj.group(1)) + '}}'

    return ' '


def get_description(desc):
    plain_desc = markdownify(desc).replace("\n", " ")
    plain_desc = ' '.join(plain_desc.split())
    plain_desc = plain_desc.replace('"', '\\"')
    return "description: \"" + plain_desc + "\"\n"


if __name__ == "__main__":
    parsed = untangle.parse("import.xml")
    posts = parsed.rss.channel.item

    create_or_empty_dir("out/")

    for post in posts:
        post_content = process_content(post.content_encoded.cdata)
        slug = post.link.cdata.replace("https://ishan.co/", "")

        to_write = front_matter.format(post.title.cdata, post.pubDate.cdata)
        to_write += get_categories_and_tags(post.category)
        to_write += "slug: {}\n".format(slug)

        if post.excerpt_encoded.cdata:
            to_write += get_description(post.excerpt_encoded.cdata)

        to_write += front_matter_end
        to_write += "\n"
        to_write += markdownify(post_content)

        # TODO: Find root cause and do replacement properly
        to_write = to_write.replace("\\_", "_")

        write_markdown_to("out/", slug, to_write)
