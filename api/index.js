export default async function handler(req, res) {
    // CORS aur Headers allow karo taaki bot requests accept ho sakein
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Content-Type', 'application/json');

    const { id } = req.query;
    if (!id) {
        return res.status(400).json({ error: "Video ID missing hai bhai!" });
    }

    try {
        // Advanced iOS Embedded Client Bypasser Route - Isko YouTube block nahi kar sakta
        const response = await fetch("https://www.youtube.com/youtubei/v1/player", {
            method: "POST",
            body: JSON.stringify({
                videoId: id,
                context: {
                    client: {
                        clientName: "IOS_EMBEDDED",
                        clientVersion: "19.14.2",
                        deviceModel: "iPhone16,1",
                        hl: "en",
                        gl: "IN",
                        osName: "iOS",
                        osVersion: "17.4.1"
                    }
                }
            }),
            headers: {
                "User-Agent": "com.google.ios.youtube/19.14.2 (iPhone16,1; U; CPU iPhone OS 17_4_1 like Mac OS X; en_US)",
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();
        const streamingData = data.streamingData || {};
        const formats = (streamingData.formats || []).concat(streamingData.adaptiveFormats || []);
        
        let url_720p = null;
        let url_360p = null;

        // Pure streaming links extract karo (googlevideo.com waale)
        for (const fmt of formats) {
            if (fmt.url) {
                if (fmt.itag === 22 || fmt.height === 720) url_720p = fmt.url;
                if (fmt.itag === 18 || fmt.height === 360) url_360p = fmt.url;
            }
        }

        // Fallback agar exact match na ho toh pehla working video format uthao
        if (!url_360p) {
            const videoFmt = formats.find(f => f.url && f.mimeType?.includes("video/mp4"));
            if (videoFmt) url_360p = videoFmt.url;
        }

        return res.status(200).json({
            title: data.videoDetails?.title || "YouTube Video",
            url_720: url_720p,
            url_360: url_360p
        });

    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
                  }
