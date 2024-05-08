def hrv_analysis(ppis, stay = True):
    global ts, pts
    ibi_diff = 0
    if len(ppis) == 0:
        oled.fill(0)
        oled.text("Measure HR first", 0, 30, 1)
        oled.show()
        time.sleep(3)
        return False
    mean_ppi = sum(ppis)/len(ppis)
    
    mean_HR = 60000/mean_ppi
    
    for ppi in ppis:
        ibi_diff += (ppi - mean_ppi)**2
    ssdn = math.sqrt(ibi_diff/len(ppis) - 1)
    
    for i in range(len(ppis) - 1):
        ibi_diff += (ppis[i] - ppis[i + 1])**2
    rmssd = math.sqrt(ibi_diff/len(ppis) - 1)
    
    measurement = {
    "mean_hr": round(mean_HR),
    "mean_ppi": round(mean_ppi),
    "rmssd": round(rmssd),
    "sdnn": round(ssdn)
    }
    if len(history_list) >= 5:
        history_list.remove(history_list[0])
    history_list.append(measurement)
    oled.fill(0)
    count = 0
    for term, measure in measurement.items():
        oled.text(f"{term}: {measure}", 0, (text_height * text_pos_magn[count]) - 3 * text_pos_magn[count], 1)
        count += 1
    oled.show()
    if stay == False:
        return measurement
    while True:
        if press.has_data():
            if ts - pts < 250:
                #print(ts - pts)
                pts = ts
                continue
            else:
                #print(ts - pts)
                pts = ts
                break
    json_message = measurement
    
    return json_message


