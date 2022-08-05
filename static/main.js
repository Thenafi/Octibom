const buttonElement = document.getElementById("button1");
const renderDivElement = document.getElementById("renderdiv");
const inputBoxElement = document.getElementById("inputbox");
const copyButtonElement = document.getElementById("buttoncopy");
const occasionDivElement = document.getElementById("occasionDiv");

const occasionFinder = function (sentence) {
  let wordsList = [
    "Anniversary",
    "Birthday",
    "Christmas",
    "Easter",
    "Engagement",
    "Father's Day",
    "Halloween",
    "Hanukkah",
    "Hen Party",
    "Mother's Day",
    "New Baby & Christenings",
    "New Year's",
    "Stag Party",
    "Valentine's Day",
    "Wedding",
    "Wedding Gifts",
  ];
  let _return_words = [];
  for (let i = 0; i < wordsList.length; i++) {
    const word = wordsList[i];
    if (sentence.toLowerCase().search(word.toLowerCase()) > 1) {
      _return_words.push(word);
    } else if (
      sentence.toLowerCase().search("valentine") > 1 ||
      sentence.toLowerCase().search("valentines") > 1 ||
      sentence.toLowerCase().search("valentine's") > 1
    ) {
      _return_words.push("Valentine's Day");
    } else if (
      sentence.toLowerCase().search("fathers day") > 1 ||
      sentence.toLowerCase().search("father") > 1 ||
      sentence.toLowerCase().search("father's") > 1
    ) {
      _return_words.push("Father's Day");
    } else if (
      sentence.toLowerCase().search("mothers day") > 1 ||
      sentence.toLowerCase().search("mother") > 1 ||
      sentence.toLowerCase().search("mother's") > 1
    ) {
      _return_words.push("Mother's Day");
    }
  }
  return _return_words;
};

const addingHtmlInDiv = function () {
  if (window.location.pathname === "/render") {
    renderDivElement.innerHTML = `${inputBoxElement.value}`;

    for (const element of occasionFinder(renderDivElement.textContent)) {
      html = `<input type="text" value="${element}"/>`;
      occasionDivElement.insertAdjacentHTML("afterbegin", html);
    }
  } else {
    const regexp = /(\d+)/g;
    renderDivElement.innerHTML = `[${inputBoxElement.value.match(regexp)}]`;
  }
};

function copyDivToClipboard() {
  var range = document.createRange();
  range.selectNode(renderDivElement);
  window.getSelection().removeAllRanges();
  window.getSelection().addRange(range);
  document.execCommand("copy");
  window.getSelection().removeAllRanges();
}
buttonElement.addEventListener("click", addingHtmlInDiv);

copyButtonElement.addEventListener("click", copyDivToClipboard);
