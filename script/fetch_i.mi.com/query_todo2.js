(async () => {
  async function query(url) {
    const exceptions = [];
    for (let i = 0; i < maxAttempts; i++) {
      try {
        return await (await fetch(url)).json();
      } catch (exception) {
        console.log("retry error")
        exceptions.push(exception);
      }
    }
    window.failures ? window.failures.push(...exceptions) : window.failures = exceptions;
    throw new Error('Too many failed trials. For more information, check out window.failures.');
  }

  const maxAttempts = 20;
  let neededToContinue = true;

  console.log('Query start.');
//   console.groupCollapsed('Notes fetched');

//   do {
    let time = (new Date()).getTime();
    let url = 'https://i.mi.com/todo/v1/user/records/0?ts=' + time;
    let sourceData = await query(url);
    const etag_list = sourceData.data.record.contentJson.sort.orders;
    console.log(etag_list);
    let total = sourceData.data.record.contentJson.sort.orders.length;
    console.log(total);
    let cnt = 0;
    let watermark_list = [];
    while (cnt < total)
    {
        watermark_list.push(etag_list[cnt]);
        cnt += 200;
    }
    console.log(watermark_list);
    for(let watermark in watermark_list) {
        time = (new Date()).getTime();
        url = 'https://i.mi.com/todo/v1/user/records?ts=' + time + '&syncToken={"syncExtraInfo":"FgAWgITIgLOTwSGGrs-uwwcByAEcERaAhMiAs5PBIRwAAAA","watermark":"' + watermark + '"}&limit=200';
        let data = await query(url);
        console.log(data.data.records);
        console.log(data.data.records[0].contentJson.entity.content);
        break;
    }
    // neededToContinue = false;
    // console.log("retry");
//   } while (neededToContinue);

  console.log('Congrats! Check out window.exportedData.');
})();