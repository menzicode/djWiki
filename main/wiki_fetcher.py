import mwparserfromhell
import pywikibot

#TODO: refactor into a server-side parser - for example, use better tags for the titles, handle tag type logic, etc.
#TODO Rust parser?

def parse(title):
    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site, title)
    text = page.get()
    return mwparserfromhell.parse(text)

def wikicode_to_doc(wikicode):
    document = []

    count = 0
    for node in wikicode.nodes:
        if isinstance(node, mwparserfromhell.nodes.Heading):
            level = node.level
            content = f"{'#' * level} {node.title.strip_code()}\n"
            document.append({"id": count, "level": level, "content": content})
            count += 1

        elif isinstance(node, mwparserfromhell.nodes.Text):
            content = node.value
            document.append({"id": count, "level": 0, "content": content})
            count += 1

        elif isinstance(node, mwparserfromhell.nodes.Wikilink):
            link = node.title.strip_code()
            name = node.text
            if not name:
                name = link
            content = f"{name},http://127.0.0.1:5000/items?title={link}"
            document.append({"id": count, "level": 1, "content": content})
            count += 1

        else:
            t = node.__class__.__name__
            content = f"Unsupported type: {t}"
            document.append({"id": count, "level": 0, "content": content})
            count += 1

    return document

def wiki_title_to_doc(title):
    wikicode = parse(title)
    return wikicode_to_doc(wikicode)

def wikicode_to_markdown(wikicode_str):
    wikicode = mwparserfromhell.parse(wikicode_str)
    markdown = ""

    for node in wikicode.nodes:

        if isinstance(node, mwparserfromhell.nodes.Heading):
            level = node.level
            markdown += f"<nl>{'#' * level} {node.title.strip_code()}<nl>"

        elif isinstance(node, mwparserfromhell.nodes.Text):
            val = node.value.replace("\n", "<nl>")
            markdown += val

        elif isinstance(node, mwparserfromhell.nodes.Wikilink):
            link = node.title.strip_code()
            name = node.text
            if node.text is None:
                name = link
            link = link.replace(" ", "_")
            markdown += f"[{name}](/wiki/{link})"

        elif isinstance(node, mwparserfromhell.nodes.ExternalLink):
            link = node.url
            markdown += f"[{link}]"

        elif isinstance(node, mwparserfromhell.nodes.HTMLEntity):
            link = node.value
            markdown += f"<ENTITY>{link}"

        elif isinstance(node, mwparserfromhell.nodes.Tag):
            text = node.contents
            markdown += f"{text}"

        elif isinstance(node, mwparserfromhell.nodes.Template):
            text = node.params
            name = node.name
            markdown += f"<nl>{name}, {text}<nl>"

    return jsonify({"markdown": markdown})

def get_main_image_link(title):
    # parse the wikitext
    wikicode = parse(title)
    wikicode = mwparserfromhell.parse(wikicode)
    
    # find the infobox
    templates = wikicode.filter_templates()
    infobox = None
    for template in templates:
        if 'infobox' in template.name.lower():
            infobox = template
            break
    
    if not infobox:
        return None
    
    # find the main image in the infobox
    for param in infobox.params:
        if 'image' in param.name.lower():
            image_name = param.value.strip()
            if image_name:
                # format the image link
                image_link = f"https://en.wikipedia.org/wiki/File:{image_name.replace(' ', '_')}"
                return image_link
    
    return None

if __name__ == '__main__':
    print(get_main_image_link("Roger Federer"))
