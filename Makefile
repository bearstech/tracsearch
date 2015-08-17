style:
	lessc --include-path=components less/styles-blue.less static/styles.css

js:
	uglifyjs --stats -o static/tracsearch.min.js static/tracsearch.js
