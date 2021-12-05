// import {micromark} from 'micromark'

// console.log(micromark('## Hello, *world*!'))


import fs from 'fs'
// import {stream} from 'micromark/stream'

import {unified} from 'unified'
import remarkParse from 'remark-parse'
import remarkGfm from 'remark-gfm'
import remarkRehype from 'remark-rehype'
import rehypeStringify from 'rehype-stringify'

let data = fs.readFileSync("example.md")

async function main() {
  const file = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype, {allowDangerousHtml: true})
    // .use(rehypeSanitize)
    .use(rehypeStringify, {allowDangerousHtml: true})
    .process(data)
    fs.writeFileSync("output.html", String(file))

  // console.log(String(file))
}
main()
