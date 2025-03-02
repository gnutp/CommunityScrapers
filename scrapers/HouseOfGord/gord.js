//
// House of Gord model scraper
//
// Quick 'n dirty Javascript to export all models from House of Gord
// into an intermediate format useable by 'gord.py'.
//
// Usage:
// * In your browser, go to https://www.houseofgord.com/models
// * Open dev console, run the script below.
// * Copy & paste the resulting JSON output into a file named 'gord.json'.
// * Follow instructions in 'gord.py'.
//
function iterateXPathResult() {
    let commonxpath = '//table[@class="participant_listing"]';
    let namexpath = './/tr[@class="participant_individual_name"]//a/text()';
    let urlxpath = './/tr[@class="participant_individual_name"]//a/@href';
    let imagexpath = './/tr[@class="participant_individual_pic"]//img';

    let nodes = document.evaluate(commonxpath, document.body, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);

    let models = [];

    try {
        let node;
        while (node = nodes.iterateNext()) {
            let name = document.evaluate(namexpath, node, null, XPathResult.STRING_TYPE)
                .stringValue.trim();
            let image = document.evaluate(imagexpath, node, null, XPathResult.FIRST_ORDERED_NODE_TYPE)
                .singleNodeValue;
            let url = document.evaluate(urlxpath, node, null, XPathResult.STRING_TYPE)
                .stringValue.replace(/^/, document.location.origin /* 'https://www.houseofgord.com/' */);

            let imageUrl = image.getAttribute("src");

            models.push({ name, image: imageUrl, url });
        }
    } catch (e) {
        console.error(`Document tree modified during iteration: ${e}`);
    }

    return models;
}

const models = iterateXPathResult();

console.log(JSON.stringify(models, null, 2));