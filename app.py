import facebook, json, cv2, pytesseract, numpy, googletrans
import urllib, random, client, time
from PIL import Image, ImageFont,ImageDraw

config = json.loads(open('keys.json', 'r').read())
captions = json.loads(open('captions.json').read())

while True:
    try:
        old_img = ''
        img = ''
        try:
            old_img = Image.open('raw.jpg')
        except:
            old_img = Image.new('RGB', (1,1))
            
        c = client.Client()
        img_url = ''
        title = ''
        translated = ''
        font = ImageFont.truetype('impact.ttf', 32)
        
        print('downloading post...')
        try:
            c.log_in(config['9gag_email'], config['9gag_password'])
        except APIException as e:
            print(e)
        else:
            for post in c.get_posts(entry_types=['photo'], count=1):
                img_url = post.get_media_url()
                title = post.title
                urllib.request.urlretrieve(img_url, 'raw.jpg')
        
        img = Image.open('raw.jpg')
        
        if old_img == img:
            print('no new post')
        else:
            print('got a new post')
            print('reading text...')
            text = pytesseract.image_to_string(img).split('\n')
        
            print('translating...')
            gs = googletrans.Translator()
            for line in text:
                if len(line) > 5:
                    translated = translated + '\n' + gs.translate(line, dest='hu').text
            title = gs.translate(title, dest='hu').text if len(translated) < 1 \
                    else captions[random.randint(0, len(captions) - 1)]
            
            boxes = pytesseract.image_to_boxes(img)
            boxes = list(filter(lambda el: el.split(' ')[0].isalpha(), boxes.split('\n')))
        
            print('masking text...')
            img_np = numpy.array(img)
            tx_top = (0, 0)
            height, _, _ = img_np.shape
            if len(boxes) > 3:
                tx_top = (int(boxes[0].split(' ')[1]), height - int(boxes[0].split(' ')[2]) - 32)
                for b in boxes[0:len(boxes)-2]:
                    s = b.split(' ')
                    x = int(s[1])
                    y = height - int(s[2])
                    w = int(s[3])
                    h = height - int(s[4])
                    img_np = cv2.rectangle(img_np, (x,y), (w, h), (255,255,255), cv2.FILLED)
        
            print('pasting watermark...')
            img_pil = Image.fromarray(img_np)
            overlay_tibi = Image.open('overlay0.png').resize((200,200))
            t_w, t_h = overlay_tibi.size
            w, h = img_pil.size
            img_pil.paste(overlay_tibi, (w-t_w, h-t_h), overlay_tibi)
            
            draw = ImageDraw.Draw(img_pil)
            draw.text(tx_top, translated.strip(), font=font, fill=(0,0,0))
            img_np = numpy.array(img_pil)
            
            #cv2.imshow('bruh', img_np)
            #cv2.waitKey()
            print('saving image...')
            cv2.imwrite('meme.jpg', img_np)
        
            print('posting to facebook...')
            page = facebook.GraphAPI(config['long_access_token'])
            page.put_photo(image=open('meme.jpg', 'rb'), message=title)
        
            #page.put_object('me', 'feed', message='h')
        print('going to sleep zzz...')
        time.sleep(config['refresh_interval'])

    except:
        continue


    