var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "91.77.161.132",
            port: parseInt("13059")
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "mas_1m1",
            password: "7256_Hgstr"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {urls: ["<all_urls>"]},
    ['blocking']
);