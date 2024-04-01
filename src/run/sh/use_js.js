//
// use js at present
//

function click_all(){
    var buttons = document.getElementsByTagName('button');
    for (var i = 0; i < buttons.length; i++) {
      var button = buttons[i];
      if (button.textContent.includes('查看全部') || button.textContent.includes('阅读作品')) {
        return button;
      }
    }
}

export click_all;

// get page height
return document.body.scrollHeight

//spider_gif_images
return window.performance.getEntriesByType('resource')