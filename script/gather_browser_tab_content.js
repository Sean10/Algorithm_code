(async function() {
  try {
    const getAllTabs = () => {
      return document.querySelectorAll('[role="tab"]');
    };

    const tabs = getAllTabs();
    
    if (tabs.length === 0) {
      console.warn('未找到任何标签页元素');
      return;
    }

    console.log(`✓ 找到 ${tabs.length} 个标签页，开始逐个提取内容...`);

    let allContent = [];
    
    for (let i = 0; i < tabs.length; i++) {
      const tab = tabs[i];
      const tabName = tab.innerText || tab.textContent || `tab-${i + 1}`;
      
      tab.click();
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const aceContent = document.querySelector('.ace_content');
      
      if (aceContent) {
        const text = aceContent.innerText || aceContent.textContent || '';
        
        if (text.trim()) {
          allContent.push(text.trim());
          console.log(`[${tabName}] ✓ 提取了 ${text.length} 个字符`);
        } else {
          console.log(`[${tabName}] ⚠ 内容为空`);
        }
      } else {
        console.warn(`[${tabName}] ⚠ 未找到 ace_content 元素`);
      }
    }

    if (allContent.length === 0) {
      console.warn('没有找到任何内容');
      return;
    }

    const mergedContent = allContent.join('\n\n');

    const blob = new Blob([mergedContent], { type: 'text/plain;charset=utf-8' });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sql-tabs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    console.log(`✓ 成功提取 ${allContent.length} 个标签页的内容，已下载文件`);
    console.log(`✓ 总字符数: ${mergedContent.length}`);
    
  } catch (error) {
    console.error('执行出错:', error);
  }
})();
