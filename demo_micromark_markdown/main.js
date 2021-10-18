// import {micromark} from 'micromark'

// console.log(micromark('## Hello, *world*!'))


import fs from 'fs'
// import {stream} from 'micromark/stream'

// fs.createReadStream('example.md')
//   .on('error', handleError)
//   .pipe(stream())
//   .pipe(process.stdout)

// function handleError(error) {
//   // Handle your error here!
//   throw error
// }




import {unified} from 'unified'
import remarkParse from 'remark-parse'
import remarkGfm from 'remark-gfm'
import remarkRehype from 'remark-rehype'
import rehypeStringify from 'rehype-stringify'

let data = fs.readFileSync("example.md")

let node = unified()
  .use(remarkParse)
//   .use(remarkGfm)
//   .use(remarkRehype)
//   .use(rehypeStringify)
  .parse(data)
//   .then((file) => {
//     console.log(file)
// })

// console.log(JSON.stringify(node, null, 4));

fs.writeFileSync("output.json", JSON.stringify(node, null, 4))