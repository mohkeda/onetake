# فيديو النتائج الشهرية (عمودي 9:16)

1. `node extract.mjs <publish/index.html> data.json` — يسحب أرقام الشهر والشهر السابق من اللوحة (عدّل الشهرين داخل الملف).
2. احسب `vdata.json` (إجمالي الشركة، المراكز، الأقسام، البراندات) وضعه مكان `/*DATA*/null` في `video.html`.
3. `node render.mjs video_built.html out.mp4` — يرسم 30 إطار/ثانية ويحوّلها MP4 بـ ffmpeg (1080×1920، 38 ثانية).

الإطار «نتائج مبدئية» يظهر أعلى الفيديو؛ احذفه بعد إقفال الشهر.

## فيديو المركز بتعليق صوتي
- center.html + vc.json (بيانات كل مركز). `D.durs` اختياري: مدة كل مشهد بالثواني لتطابق التعليق الصوتي.
- التعليق من ElevenLabs (صوت Sultan السعودي)، ثم: `ffmpeg -i video.mp4 -i vo.mp3 -filter_complex "[1:a]adelay=200|200,apad[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -shortest out.mp4`.
- حدود المشاهد = فترات الصمت بين فقرات النص (ffmpeg silencedetect).
