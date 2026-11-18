VoxBangla Voice Typing - GitHub Actions Build Package
======================================================

এই প্যাকেজে GitHub Actions workflow যুক্ত আছে। এটি GitHub-এর Windows runner-এ
Python 3.11 এবং PyInstaller ব্যবহার করে VoxBangla.exe তৈরি করবে। আপনার নিজের
Windows কম্পিউটারে Python ইনস্টল করার দরকার হবে না। Build machine-এ Python
শুধু GitHub-এর runner-এ ব্যবহৃত হয়; তৈরি EXE-তে Python runtime bundle হয়।

GitHub দিয়ে EXE তৈরি করার নিয়ম
------------------------------
১. https://github.com এ সাইন ইন করুন।
২. New repository তৈরি করুন; নাম দিন VoxBangla (Public অথবা Private যেকোনোটি)।
৩. এই ZIP Extract করুন। Extract করা ফোল্ডারের ভেতরের সব ফাইল ও .github ফোল্ডার
   repository-র মূল জায়গায় Upload files দিয়ে আপলোড করুন।
   খেয়াল রাখবেন: .github/workflows/build-windows.yml ফাইলটি যেন ঠিক এই path-এ থাকে।
৪. Commit changes চাপুন। main branch-এ push হলে build স্বয়ংক্রিয়ভাবে শুরু হবে।
৫. Repository-র Actions tab খুলুন → Build VoxBangla for Windows workflow নির্বাচন করুন।
৬. Workflow run সম্পন্ন হলে run-এর পাতার নিচের Artifacts অংশ থেকে
   VoxBangla-Windows-x64 ডাউনলোড করুন।
৭. ZIP Extract করে VoxBangla.exe চালান। ব্যবহারকারীর PC-তে Python লাগবে না।

নিজে হাতে Build চালাতে চাইলে
----------------------------
Actions tab → Build VoxBangla for Windows → Run workflow → Run workflow।

কাজ / ফিচার
-----------
- বাংলা (বাংলাদেশ) ও English (US) voice recognition
- Avro / Unicode, Bijoy Unicode, Bijoy Classic (ANSI) output options
- সক্রিয় অ্যাপে Ctrl+V দিয়ে শনাক্ত করা লেখা পাঠানোর অপশন
- সম্পাদনাযোগ্য transcript, clipboard copy, TXT save

গুরুত্বপূর্ণ সীমাবদ্ধতা ও গোপনীয়তা
--------------------------------
- বর্তমান সংস্করণে SpeechRecognition-এর Google Speech Recognition web service ব্যবহৃত হয়।
  ইন্টারনেট আবশ্যক এবং স্বীকৃতির জন্য অডিও Google-এর সার্ভিসে পাঠানো হয়।
- SpeechRecognition-এর default Google key পরীক্ষামূলক/ব্যক্তিগত ব্যবহারের জন্য;
  এটি কোনো স্থায়ী বা বাণিজ্যিক API নিশ্চয়তা নয়।
- Avro / Unicode এবং Bijoy Unicode অপশনে standard Unicode টেক্সট তৈরি হয়।
- Bijoy Classic (ANSI) অপশনে পুরোনো Bijoy/SutonnyMJ-compatible ANSI encoding লাগে;
  এটি সাধারণ Unicode ওয়েব ফর্মে ব্যবহার করবেন না।
- Auto typing চালু থাকলে সক্রিয় অ্যাপেই Ctrl+V করা হবে। কথা বলার আগে সঠিক
  অ্যাপে এবং সঠিক cursor position-এ focus আছে কি না নিশ্চিত করুন।
- Build সফল হওয়া মানেই সব Windows PC-তে microphone ও paste পরীক্ষা সম্পন্ন হয়েছে
  এমন নয়। প্রথমবার চালানোর সময় Windows microphone permission দিন।

সমস্যা হলে
----------
- GitHub build ব্যর্থ হলে Actions → failed run → Build Windows x64 EXE ধাপের log দেখুন।
- microphone error হলে Windows Settings → Privacy & security → Microphone-এ
  desktop apps-এর microphone access চালু করুন।
- Bijoy Classic লেখা সঠিক না দেখালে গন্তব্য অ্যাপে SutonnyMJ বা সামঞ্জস্যপূর্ণ
  Bijoy ANSI font নির্বাচন করুন।

লাইসেন্স / তৃতীয় পক্ষ
--------------------
এই প্যাকেজ Avro Keyboard, Bijoy Keyboard বা কোনো proprietary font বিতরণ করে না।
NOTICE.txt-এ third-party components-এর সংক্ষিপ্ত তথ্য রয়েছে।
