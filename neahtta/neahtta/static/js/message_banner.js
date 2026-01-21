//var tnn_current_lang = "en";
//var tnn_notice_ru = "извещение";
var tnn_notice_en = "Notice";
var tnn_message_en = "Neahttadigisanit will be unavailable for around one hour on the morning of Friday, 23rd of January, 2026, due to infrastructure changes.";
//var tnn_message_ru = "Neahttadigisanit будет недоступен вечером DATE.";
//var tnn_in_english = "English";
//var tnn_in_russian = "на русском";

// https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API
function tnn_storageAvailable(type) {
  var storage;
  try {
    storage = window[type];
    var x = "__storage_test__";
    storage.setItem(x, x);
    storage.removeItem(x);
    return true;
  } catch (e) {
    return (
      e instanceof DOMException &&
      // everything except Firefox
      (e.code === 22 ||
        // Firefox
        e.code === 1014 ||
        // test name field too, because code might not be present
        // everything except Firefox
        e.name === "QuotaExceededError" ||
        // Firefox
        e.name === "NS_ERROR_DOM_QUOTA_REACHED") &&
      // acknowledge QuotaExceededError only if there's something already stored
      storage &&
      storage.length !== 0
    );
  }
}
function tnn_close_notice() {
    var el = document.getElementById("tnn-maintainance-notice");
    document.body.removeChild(el);

    if (tnn_storageAvailable("sessionStorage")) {
        window.sessionStorage.setItem("tnn-notice-seen", "yes");
    }
}
//function tnn_change_lang() {
//    var msg = document.getElementById("tnn-notice-msg");
//    var notice = document.getElementById("tnn-notice-notice");
//    var in_lang = document.getElementById("tnn-notice-changelang-btn");
//
//    if (tnn_current_lang == "en") {
//        tnn_current_lang = "ru";
//        msg.innerText = tnn_message_ru;
//        notice.innerText = tnn_notice_ru;
//        in_lang.innerText = tnn_in_english;
//    } else {
//        tnn_current_lang = "en";
//        msg.innerText = tnn_message_en;
//        notice.innerText = tnn_notice_en;
//        in_lang.innerText = tnn_in_russian;
//    }
//}

// use javascript to not show the banner, if they have clicked it away already
// this session
document.addEventListener("DOMContentLoaded", function() {
    window.tnn_close_notice = tnn_close_notice;

    if (tnn_storageAvailable("sessionStorage")) {
        var item = window.sessionStorage.getItem("tnn-notice-seen");
        if (item !== null) {
            tnn_close_notice();
        }
    }
});
