https://www.apple.com.cn/shop/updateSEO?m={"filterMap":[{"refurbClearModel":"macbookpro"},          {"tsMemorySize":"32gb"},{"tsMemorySize":"64gb"}],"refererUrl":"https://www.apple.com.cn/shop/refurbished/mac/macbook-pro-32gb"}


https://www.apple.com.cn/shop/updateSEO?m={"filterMap":[{"refurbClearModel":"macbookpro"},{"tsMemorySize":"32gb"},{"dimensionScreensize":"16inch"}],"refererUrl":"https://www.apple.com.cn/shop/refurbished/mac/macbook-pro-32gb"}

当不存在匹配结果的时候, 应该是直接返回

``` json
{"head":{"status":"200","data":{}}}
```

有结果的时候

``` json
{
    "head": {
        "status": "200",
        "data": {}
    },
    "body": {
        "marketingData": {
            "serviceResponseFailed": false,
            "curatedKit": false,
            "canonicalURL": "https://www.apple.com.cn/shop/refurbished/mac/2020-13-英寸-macbook-pro",
            "targetURL": "https://www.apple.com.cn/shop/refurbished/mac/2020-13-英寸-macbook-pro",
            "microdataList": [],
            "socialSharingTags": {
                "items": [
                    {
                        "index": 0,
                        "value": {
                            "type": "property",
                            "typeValue": "og:locale",
                            "content": "zh_CN"
                        },
                        "last": false,
                        "even": true,
                        "position": 1,
                        "first": true
                    },
                    {
                        "index": 1,
                        "value": {
                            "type": "property",
                            "typeValue": "og:type",
                            "content": "website"
                        },
                        "last": false,
                        "even": false,
                        "position": 2,
                        "first": false
                    },
                    {
                        "index": 2,
                        "value": {
                            "type": "name",
                            "typeValue": "robots",
                            "content": "noindex, nofollow"
                        },
                        "last": false,
                        "even": true,
                        "position": 3,
                        "first": false
                    },
                    {
                        "index": 3,
                        "value": {
                            "type": "name",
                            "typeValue": "twitter:site",
                            "content": "@apple"
                        },
                        "last": false,
                        "even": false,
                        "position": 4,
                        "first": false
                    },
                    {
                        "index": 4,
                        "value": {
                            "type": "property",
                            "typeValue": "og:site_name",
                            "content": "Apple (中国大陆)"
                        },
                        "last": false,
                        "even": true,
                        "position": 5,
                        "first": false
                    },
                    {
                        "index": 5,
                        "value": {
                            "type": "name",
                            "typeValue": "twitter:card",
                            "content": "summary_large_image"
                        },
                        "last": false,
                        "even": false,
                        "position": 6,
                        "first": false
                    },
                    {
                        "index": 6,
                        "value": {
                            "type": "property",
                            "typeValue": "og:description",
                            "content": "选购完美如新的翻新品 Mac，比较不同型号。 网上购买，享有免费送货服务及一年保修。 所有翻新产品都有 Apple 测试和认证。"
                        },
                        "last": false,
                        "even": true,
                        "position": 7,
                        "first": false
                    },
                    {
                        "index": 7,
                        "value": {
                            "type": "property",
                            "typeValue": "og:image",
                            "content": "https://as-images.apple.com/is/og-default?wid=1200&hei=630&fmt=jpeg&qlt=95&op_usm=0.5,0.5&.v=1525370171638"
                        },
                        "last": false,
                        "even": false,
                        "position": 8,
                        "first": false
                    },
                    {
                        "index": 8,
                        "value": {
                            "type": "property",
                            "typeValue": "og:url",
                            "content": "https://www.apple.com.cn/shop/refurbished/mac/2020-13-英寸-macbook-pro"
                        },
                        "last": false,
                        "even": true,
                        "position": 9,
                        "first": false
                    },
                    {
                        "index": 9,
                        "value": {
                            "type": "property",
                            "typeValue": "og:title",
                            "content": "翻新 Mac - 2020 - 13 英寸 - MacBook Pro - Apple (中国大陆)"
                        },
                        "last": true,
                        "even": false,
                        "position": 10,
                        "first": false
                    }
                ],
                "size": 10
            }
        }
    }
}
```

# Reference
1. [python 3\.x \- How to disable automatic redirects in python3 urllib\.request? \- Stack Overflow](https://stackoverflow.com/questions/52086805/how-to-disable-automatic-redirects-in-python3-urllib-request)