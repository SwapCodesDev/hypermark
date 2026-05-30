# Markdown Cheat Sheet

Thanks for visiting [The Markdown Guide](https://www.markdownguide.org)!

This Markdown cheat sheet provides a quick overview of all the Markdown syntax elements. It can’t cover every edge case, so if you need more information about any of these elements, refer to the reference guides for [basic syntax](https://www.markdownguide.org/basic-syntax/) and [extended syntax](https://www.markdownguide.org/extended-syntax/).

## Basic Syntax

These are the elements outlined in John Gruber’s original design document. All Markdown applications support these elements.

### Heading

# H1
## H2
### H3
#### H4
##### H5
###### H6

### Bold

**bold text**

### Italic

*italicized text*

### Blockquote

> blockquote

### Ordered List

1. First item
  1. indent
    1. indent two
  2. indent
2. Second item
3. Third item

### Unordered List

- First item
  - indent
- Second item
  - indent
    - more indent
  - indent
- Third item

### Code

`code`

### Horizontal Rule

---

### Link

[Markdown Guide](https://www.markdownguide.org)

### Image

![alt text](https://www.markdownguide.org/assets/images/tux.png)

## Extended Syntax

These elements extend the basic syntax by adding additional features. Not all Markdown applications support these elements.

### Table

| Syntax | Description | More |
| ----------- | ----------- | ------ |
| Header | Title |
| Paragraph | Text |

### Fenced Code Block

``` python
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```

### Footnote

Here's a sentence with a footnote. [^a]

[^a]: This is the footnote.


### Heading ID

### My Great Heading {#custom-id}

### Definition List

term 1
: definition 1
: definition 2


### Strikethrough

~~The world is flat.~~

### Task List

- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media

### Emoji

That is so funny! :joy:

(See also [Copying and Pasting Emoji](https://www.markdownguide.org/extended-syntax/#copying-and-pasting-emoji))

### Highlight

I need to highlight these ==very important words==.

### Subscript

H~2~O

### Superscript

X^2^

## Modern Extensions

### Fenced Alert Containers

::: note Informational Note
This is a standard note banner used to highlight helpful information.
:::

::: warning CRITICAL WARNING!
This is a warning block to highlight important cautions.
:::

::: tip Best Practice
This is a tip callout box to highlight suggestions.
:::

### Interactive Spoilers

Do you want to know the secret? ||Hypermark is ultra fast and style-injected!||
