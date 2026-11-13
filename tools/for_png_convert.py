from PIL import Image

def process_sprite_auto(input_path, output_path, target_size=(80, 80), tolerance=90):
    # Открываем изображение и переводим в RGBA
    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()
    
    # Автоматически берем цвет фона из самого верхнего левого пикселя
    bg_pixel = img.getpixel((0, 0))
    br, bg, bb = bg_pixel[0], bg_pixel[1], bg_pixel[2]
    
    new_data = []
    for item in data:
        r, g, b, a = item
        # Считаем разницу цветов (евклидово расстояние)
        color_diff = ((r - br) ** 2 + (g - bg) ** 2 + (b - bb) ** 2) ** 0.5
        
        # Если цвет близок к цвету в углу, делаем пиксель невидимым
        if color_diff < tolerance:
            new_data.append((0, 0, 0, 0))  # Полная прозрачность
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # Масштабируем без размытия, сохраняя пиксели (Nearest Neighbor)
    img_resized = img.resize(target_size, resample=Image.Resampling.NEAREST)
    img_resized.save(output_path, "PNG")
    print(f"Готово! Спрайт сохранен как {output_path} (64x64, фон вырезан автоматически)")

# Как запустить (просто укажите имя скачанного файла и как его сохранить):
if __name__ == "__main__":
    import os
    if os.path.exists("dem.jpg"):
        process_sprite_auto("dem.jpg", "shotgun_0.png")