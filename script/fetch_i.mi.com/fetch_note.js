(async () => {
    /**
     * Replaces :attribute: with the corresponding attribute and converts :: to :.
     * 
     * @param string The string pending to be proceeded.
     * @param attributes The attributes pending to be replaced with.
     */
    function substitute(string, attributes = {}) {
        let output = '';
        let currentAttribute = '';
        let isInAttribute = false;
      
        for (let char of string) {
          if (char === ':') {
            isInAttribute = !isInAttribute;
            if (!isInAttribute) {
              output += attributes.hasOwnProperty(currentAttribute)
                ? attributes[currentAttribute]
                : `:${currentAttribute}:`;
              currentAttribute = '';
            }
          } else if (isInAttribute) {
            currentAttribute += char;
          } else {
            output += char;
          }
        }
      
        return output;
    }
    /**
     * Fetches an image as data URL.
     * Reference: https://www.cnblogs.com/cyfeng/p/16107747.html
     * 
     * @param id The image ID.
     */
    async function fetchImage(id) {
        let image;

        {
            const exceptions = [];
            for(let i = 0; i < maxAttempts; i++) {
                try {
                    image = new Image();
                    /**
                     * Tainted canvases may not be exported.
                     * See https://www.cnblogs.com/iroading/p/11011268.html.
                     */
                    image.setAttribute('crossOrigin', 'anonymous');
                    image.src = substitute(urls['image'], { id });
                    await new Promise((resolve, reject) => {
                        image.addEventListener('load', resolve);
                        image.addEventListener('error', reject);
                    });
                    break;
                } catch(exception) {
                    exceptions.push(exception);
                }
            }
            if(exceptions.length) { //Remember !![] === true.
                window.failures ? window.failures.push(...exceptions) : window.failures = exceptions;
                throw new Error('Too many failed trials. For more information, check out window.failures.');
            }
        }

        const canvas = document.createElement('canvas');
        const { width, height } = image;
        canvas.width = width;
        canvas.height = height;
        canvas.getContext('2d').drawImage(image, 0, 0, width, height);
        return canvas.toDataURL('image/png');
    }
    
    /**
     * Requests a page and returns the result in JSON.
     * If failed, the request will be retried for `maxAttempts` time(s).
     * 
     * @param key The key of the URL in the var `urls`.
     * @param attributes Attributes.
     */
    async function query(key, attributes = {}) {
        const exceptions = [];
        for(let i = 0; i < maxAttempts; i++) {
            try {
                return await (await fetch(substitute(urls[key], {
                    time: (new Date()).getTime(),
                    ...attributes
                }))).json();
            }
            catch(exception) {
                exceptions.push(exception);
            }
        }
        window.failures ? window.failures.push(...exceptions) : window.failures = exceptions;
        throw new Error('Too many failed trials. For more information, check out window.failures.');
    }

    const urls = {
        list: '/note/full/page/?ts=:time:&limit=200',
        listWithSyncTag: '/note/full/page/?ts=:time:&limit=200&syncTag=:syncTag:',
        note: '/note/note/:id:/?ts=:time:',
        image: '/file/full?type=note_img&fileid=:id:'
    };
    const maxAttempts = 20;
    let folders = [];
    let notes = [];
    let images = [];
    let syncTag;
    let neededToContinue = true;

    console.log('Query start.');
    console.groupCollapsed('Notes fetched');
    do {
        const { data } = await query(syncTag ? 'listWithSyncTag' : 'list', { syncTag });
        if(data.folders) folders.push(...data.folders);
        console.log(folders.length, ' table(s) found:');
        console.log(folders.forEach(({ subject }) => subject));
        for(let { id } of data.entries) {
            const { data: { entry: noteData } } = await query('note', { id });
            //Request the referenced images simultaneously.
            for(let line of noteData.content.replace(/\<0\/\>\<.*?\/\>/g, '').split('\n'))
                if (line.startsWith('☺ ')) images.push({
                    id: line.substr(2),
                    image: await fetchImage(line.substr(2))
                });
            notes.push(noteData);
            console.count('note');
            console.log('Retrieved note:', noteData?.snippet?.substr?.(0, 20));
        }
        neededToContinue = data.entries.length;
        syncTag = data.syncTag;
    } while(neededToContinue); //the variable `data` can't be references here. Damn it!

    console.groupEnd('Notes fetched');
    window.exportedData = {
        folders,
        notes,
        images
    };
    console.log('Congrats! Check out window.exportedData.');

    function convertTimestamp(timestamp) {
        const date = new Date(timestamp);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}${month}${day}-${hours}${minutes}${seconds}`;
      }

    var importJs=document.createElement('script') 
    importJs.setAttribute("type","text/javascript") 
    importJs.setAttribute("src", "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.0/jszip.min.js")
    document.getElementsByTagName("head")[0].appendChild(importJs)
    var importFileSaver=document.createElement('script') 
    importFileSaver.setAttribute("type","text/javascript") 
    importFileSaver.setAttribute("src", "https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.4/FileSaver.js")
    document.getElementsByTagName("head")[0].appendChild(importFileSaver)

    let files2 = [];
    for (let note of window.exportedData.notes) {
        const name_val = convertTimestamp(note["createDate"]) + note["snippet"].slice(0,10).replace(' ', '_') + '.md'
        obj = {name: name_val, content: note["content"]}
        console.log(name_val)

        files2.push(obj)
    }

    // 前端处理并打包文件
    // zip = new JSZip();
    let zip2 = new JSZip();
    files2.forEach((file) => zip2.file(file.name, file.content));

    // 生成压缩包并下载
    zip2.generateAsync({type: "blob"}).then((content) => {
    saveAs(content, "files.zip");
    });
})();