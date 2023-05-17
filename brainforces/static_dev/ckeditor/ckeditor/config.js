/**
 * @license Copyright (c) 2003-2022, CKSource Holding sp. z o.o. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
};

CKEDITOR.on('instanceReady', function (ev) {
    ev.editor.dataProcessor.htmlFilter.addRules({
        elements: {
            $: function (element) {
                if (element.name == 'img') {
                    var style = element.attributes.style || '';
                    if (!style.match(/max-width/)) {
                        style += ';max-width: 100%';
                    }
                    if (!style.match(/max-height/)) {
                        style += ';max-height: 100%';
                    }
                    element.attributes.style = style;
                }
            }
        }
    });
});
