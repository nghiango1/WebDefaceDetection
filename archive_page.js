import puppeteer from 'puppeteer';
import fse from 'fs-extra'; // v 5.0.0
import path from 'path';
import fetch from 'node-fetch';
import crypto from 'crypto';

const hash = crypto.createHash('sha256');
const CAP_DEBUG_ULR_LENGTH = 40 //capture all
const FAIL_URL = path.resolve('fail-log.csv') //capture all

async function saveResponsedFile(SAVED_PATH, response, recvData, isFetch) {
	let type = '';
	let hash = crypto.createHash('sha256').update(recvData).digest('hex');
	let fileSavePath = path.resolve(SAVED_PATH, 'saved_responsed_file', hash)
	try {
		type = response.headers()['content-type'];
	}
	catch (e) {
		console.log('Get response file type error, e:', e);
	}
	try {
		// await fse.outputFile(path.resolve(SAVED_PATH,'saved_responsed_file' , hash), recvData);
		await fse.appendFile(path.resolve(SAVED_PATH, 'url_hash_log.csv'), '\n"' + response.url() + '","' + hash + '","' + type + '","' + recvData.length + '","' + isFetch + '"');
		// console.log("response url:", response.url().substr(0, CAP_DEBUG_ULR_LENGTH), "\n	hash:", hash, "\n	dir:",fileSavePath);		
	}
	catch (e) {
		console.log('File save error, get e:', e);
		console.log('	|Saved ', path.resolve(SAVED_PATH, 'saved_responsed_file', crypto.createHash('sha256').update(recvData).digest('hex')));
		console.log('	|URL ', response.url());
	}
}

/**
* @archiveUrlString duong dan den trang web, yeu cau co http:// hoac https://
**/
async function archiveFunc(archiveUrlString) {
	const START_TIME = new Date();
	let STD_REQUEST_LOG_PATH;
	let STD_URL_HASH_PATH;
	let SAVED_PATH;
	let archiveUrl;
	let archiveUrlStatus;
	let TIMEOUT_FLAG = false;
	/**
	* Xu ly dau vao
	*	Temp_name (thay toan bo ky tu :/\*?<>| bang _)
	*	Tao diem luu rieng biet cho URL
	*/
	try {
		archiveUrl = new URL(archiveUrlString);
	}
	catch (e) {
		console.log('URL Error, get ', e);
		return 1;
	}

	/** make dir 
	*	Tao Duong dan de luu file
	*/
	let temp_name = archiveUrlString.replace(/:|\/|\\|\*|\?|\"\<|\>|\|/g, '_');
	SAVED_PATH = path.resolve('saved', temp_name);
	console.log(SAVED_PATH);
	try {
		await fse.ensureDir(SAVED_PATH);
	}
	catch (e) {
		console.log('Create path error, get ', e, '\nPATH:', SAVED_PATH);
		return 2;
	}

	STD_REQUEST_LOG_PATH = path.resolve(SAVED_PATH, 'archived_log.csv');
	STD_URL_HASH_PATH = path.resolve(SAVED_PATH, 'url_hash_log.csv');
	let STD_TITLE_FEATURE_PATH = path.resolve(SAVED_PATH, 'title_log.csv');
	let STD_TEXT_ONLY_PATH = path.resolve(SAVED_PATH, 'text_only_index_loaded.html.txt');

	try {
		await fse.writeFile(STD_REQUEST_LOG_PATH, 'timestamp,type,url,status')
		await fse.writeFile(STD_URL_HASH_PATH, 'url,hash,content-type,length,isFetch')
		await fse.remove(STD_TEXT_ONLY_PATH)
	}
	catch (e) {
		console.log('Initilize log file problem, Error:', e);
		return 3;
	}
	/**  
	*	Tao puppeteer browser, 20s dong, truy cap archive URL
	*/
	const browser = await puppeteer.launch();
	// const browser = await puppeteer.launch({headless: false}); // DEBUG
	setTimeout(async () => {
		if (TIMEOUT_FLAG == false) {
			TIMEOUT_FLAG = true;
			try {
				fse.outputFile(STD_TITLE_FEATURE_PATH, await page.title() + '\n' + page.url());
				console.log('Archive url status:', archiveUrlStatus);
				const html = await page.content();
				let fileSavePath = path.resolve(SAVED_PATH, `index_loaded.html`);
				await fse.outputFile(fileSavePath, html);
				if ((await page.$eval('html', e => e.innerText)).length != 0)
					fse.appendFile(STD_TEXT_ONLY_PATH, await page.$eval('html', e => e.innerText));
				if ((await page.title()).length != 0)
					fse.appendFile(STD_TEXT_ONLY_PATH, await page.title());
			}
			catch (e) {
				console.log('Content error, proablly browser already be close, get e:', e.message);
				await browser.close();
				return (5);

			}
			await browser.close();
			return 0;
		}
	}, 5000 * 6); //30s cho moi browser

	const page = await browser.newPage();
	try {
		await page.setRequestInterception(true);
		await page.setDefaultNavigationTimeout(0);
	}
	catch (e) {
		console.log('setRequestInterception error, get e:', e);
		await browser.close();
		return 3;
	}

	page.on('dialog', async dialog => {
		if (dialog.message().length != 0)
			fse.appendFile(STD_TEXT_ONLY_PATH, dialog.message());
		await dialog.dismiss();
	});

	page.on('request', request => {
		const urlString = request.url();
		// console.log('Send request to url:  ', urlString.substr(0, CAP_DEBUG_ULR_LENGTH));
		fse.appendFile(STD_REQUEST_LOG_PATH, '\n"' + (new Date() - START_TIME).toString() + '","Request","' + urlString + '","Sent"');
		request.continue();
	});

	page.on('requestfailed', request => {
		const urlString = request.url();
		// console.log('Failed request url:   ', urlString.substr(0, CAP_DEBUG_ULR_LENGTH));
		fse.appendFile(STD_REQUEST_LOG_PATH, '\n"' + (new Date() - START_TIME).toString() + '","Request","' + urlString + '","Failed"');

	});

	page.on('requestfailed', request => {
		const urlString = request.url();
		// console.log('Failed request url:   ', urlString.substr(0, CAP_DEBUG_ULR_LENGTH));
		fse.appendFile(STD_REQUEST_LOG_PATH, '\n"' + (new Date() - START_TIME).toString() + '","Request","' + urlString + '","Failed"');

	});

	page.on('response', async (response) => {
		const request = response.request();
		const urlString = request.url();
		const url = new URL(urlString);
		const status = response.status();
		/**
		* recvData chua du lieu do server truyen ve may tinh, su dung puppeteer hoac fetch
		*/
		try {
			if ((await response.buffer()).length > 0)
				saveResponsedFile(SAVED_PATH, response, await response.buffer(), false);
			// console.log("response url:", urlString.substr(0, CAP_DEBUG_ULR_LENGTH), "buffer:\n", response.buffer());
		}
		catch (e) {
			if (e.message == 'Response body is unavailable for redirect responses') {
				console.log("Error:", e.message)
			}
			else {
				console.log('Puppeteer fail to get response.buffer() from url:', urlString.substr(0), '\n	|try fetch the resource\n	|Error:', e.message);
				await fetch(urlString)
					.then(res => res.text())
					.then(body => {
						saveResponsedFile(SAVED_PATH, response, body, true);
						// console.log("response url:", urlString.substr(0, CAP_DEBUG_ULR_LENGTH), "buffer:\n", body);
					})
					.catch(function(e) {
						console.log('Fetch error, skiping url:', urlString, '\n	|Error:', e.message);
					});;
			}
		}
		// console.log('Recv response from url:', urlString.substr(0, CAP_DEBUG_ULR_LENGTH), 'status:', status, 'data:', recvData);
		fse.appendFile(STD_REQUEST_LOG_PATH, '\n"' + (new Date() - START_TIME).toString() + '","Response","' + urlString + '","' + status + '"')

		if (url.href == archiveUrlString || url.href == page.url()) {
			archiveUrlStatus = status;
			try {
				if ((await response.buffer()).length != 0) {
					await fse.outputFile(path.resolve(SAVED_PATH, 'index.html'), await response.buffer());
					await fse.outputFile(path.resolve(SAVED_PATH, 'saved_responsed_file', crypto.createHash('sha256').update(await response.buffer()).digest('hex')), await response.buffer());
					console.log('Saved archiveUrl main index file:', path.resolve(SAVED_PATH, 'index.html'));
				}
			}
			catch (e) {
				console.log('Try save main page response error \n	|Error:', e.message);
			}
		}
	})

	try {
		await page.goto(archiveUrl.href, {
			waitUntil: 'networkidle2'
		});

	}
	catch (e) {
		console.log('Page goto error, get e:', e);
		await browser.close();
		return (4);
	}

	setTimeout(async () => {
		if (TIMEOUT_FLAG == false) {
			TIMEOUT_FLAG = true;
			try {
				fse.outputFile(STD_TITLE_FEATURE_PATH, await page.title() + '\n' + page.url());
				console.log('Archive url status:', archiveUrlStatus);
				const html = await page.content();
				let fileSavePath = path.resolve(SAVED_PATH, `index_loaded.html`);
				await fse.outputFile(fileSavePath, html)
				if ((await page.$eval('html', e => e.innerText)).length != 0)
					fse.appendFile(STD_TEXT_ONLY_PATH, await page.$eval('html', e => e.innerText));
				if ((await page.title()).length != 0)
					fse.appendFile(STD_TEXT_ONLY_PATH, await page.title());
			}
			catch (e) {
				console.log('Content error, get e:', e);
				await browser.close();
				return (5);
			}
			await browser.close();
			return 0;
		}
	}, 5000 * 3);
}


async function main() {
	let all_urls;
	all_urls = (await fse.readFile('200-safe-vn.csv', 'utf-8')).split('\r\n');
	for (let current of all_urls) {
		console.log('============Starting==============\n\t', current, '\n==================================');
		try {
			if (await archiveFunc(current) > 0) {
				fse.appendFile(FAIL_URL, current);
			}
		}
		catch (e) {
			console.log('Archive url:', current, ' process gone wroong\nError:', e);
			fse.appendFile(FAIL_URL, current + '\n');
		}
	};
}

// string = 'http://zonehmirrors.org/defaced/2013/10/20/mysafetyshop.net/root.html';
// console.log(archiveFunc(string));
main()
