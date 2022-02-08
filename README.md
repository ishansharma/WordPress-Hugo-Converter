## A Simple WordPress to Hugo Markdown Converter

This is the converter I used to migrate [my blog](https://ishan.co) from WordPress to Hugo. 

### What the script does
1. Converts all items to markdown. Assumes that all items have categories, content.
2. Converts Git gists, Twitter and YouTube embeds to Hugo shortcodes. For gists, 3 formats are supported, YouTube and Twitter only support URL on their own line.  
```
[embed]https://gist.github.com/ishansharma/11d4569830b6fc0322a1a7cc171e3c2b[/embed]
[gist]https://gist.github.com/ishansharma/f765bfede3199c285393382e4f42b2bd[/gist]
https://gist.github.com/ishansharma/eb7f0fc05dc79312098952e319515095

https://twitter.com/allymacdonald/status/1024656834571976705

https://www.youtube.com/watch?v=T5Xx3MdqdgM
```
3. Names the files same as post link. This allows you to keep same permalink structure in Hugo using `filename` permalinks:
```yaml
permalinks:
  posts: /:filename
```

### What the script does not do
1. Import images. I just downloaded `wp-content/uploads/` directory from WordPress install to Hugo's `static` directory.
2. Change image alignment in markup or `[caption]` shorttags.
3. Import comments. I'll probably move to [Talkyard](https://www.talkyard.io/blog-comments) but I didn't hve time with the initial import.

### How to use
1. Make sure you have Python 3.8 or newer. 
2. Copy the `main.py` script or entire repo locally.
3. Replace the domain in `main.py` with your domain: `link = post.link.cdata.replace("https://ishan.co/", "")`
4. Install `untangle` and `markdownify` using `pip install untangle` and `pip install markdownify`
5. Rename your WordPress post export to `import.xml` and place it in same folder as `main.py`
6. Make sure there's no folder named `out` in same folder. The script outputs markdown files there and clears the folder every time it runs.
7. Run with `python -m main.py`

