# coding: utf-8
"""Viewer-owned text. Map names and external sections keep their own translations."""

_EVENT_LABELS = {
  'en': (u'Dynamic events', u'Event %d: %s', u'Play / replay', u'Pause'),
  'ru': (u'Динамические события', u'Событие %d: %s', u'Воспроизвести / повторить', u'Пауза'),
  'pl': (u'Zdarzenia dynamiczne', u'Zdarzenie %d: %s', u'Odtwórz / powtórz', u'Pauza'),
  'de': (u'Dynamische Ereignisse', u'Ereignis %d: %s', u'Abspielen / wiederholen', u'Pause'),
  'cs': (u'Dynamické události', u'Událost %d: %s', u'Přehrát / opakovat', u'Pozastavit'),
  'uk': (u'Динамічні події', u'Подія %d: %s', u'Відтворити / повторити', u'Пауза'),
  'fr': (u'Événements dynamiques', u'Événement %d : %s', u'Lire / rejouer', u'Pause'),
  'es': (u'Eventos dinámicos', u'Evento %d: %s', u'Reproducir / repetir', u'Pausa'),
  'it': (u'Eventi dinamici', u'Evento %d: %s', u'Riproduci / ripeti', u'Pausa'),
  'tr': (u'Dinamik olaylar', u'Olay %d: %s', u'Oynat / tekrarla', u'Duraklat'),
  'hu': (u'Dinamikus események', u'%d. esemény: %s', u'Lejátszás / ismétlés', u'Szünet'),
}

_HANGAR_LABELS = {
  'en': u'Hangar', 'ru': u'Ангар', 'pl': u'Garaż',
  'de': u'Garage', 'cs': u'Garáž', 'uk': u'Ангар',
  'fr': u'Garage', 'es': u'Garaje', 'it': u'Officina',
  'tr': u'Garaj', 'hu': u'Garázs',
}

_MODE_LABELS = {
  'en': (u'Event', u'Waffenträger'),
  'ru': (u'Событие', u'Ваффентрагер'),
  'pl': (u'Wydarzenie', u'Waffenträger'),
  'de': (u'Event', u'Waffenträger'),
  'cs': (u'Událost', u'Waffenträger'),
  'uk': (u'Подія', u'Ваффентрагер'),
  'fr': (u'Événement', u'Waffenträger'),
  'es': (u'Evento', u'Waffenträger'),
  'it': (u'Evento', u'Waffenträger'),
  'tr': (u'Etkinlik', u'Waffenträger'),
  'hu': (u'Esemény', u'Waffenträger'),
}

_SCENE_KEYS = ('hangarScenes', 'hangarScene', 'hangarScene_default',
        'hangarScene_customization', 'hangarScene_overview',
        'hangarScene_armor', 'hangarScene_victory', 'hangarScene_defeat',
        'hangarScene_missions', 'hangarScene_pet')
_SCENE_LABELS = {
  'en': (u'Hangar scenes', u'Scene', u'Standard', u'Customization',
      u'Vehicle overview', u'Armor inspection', u'After battle: victory',
      u'After battle: defeat', u'Personal missions', u'Pet den'),
  'ru': (u'Сцены ангара', u'Сцена', u'Обычный', u'Кастомизация',
      u'Обзор техники', u'Осмотр брони', u'После боя: победа',
      u'После боя: поражение', u'Личные задачи', u'Питомник'),
  'pl': (u'Sceny garażu', u'Scena', u'Standardowy', u'Personalizacja',
      u'Przegląd pojazdu', u'Inspekcja pancerza', u'Po bitwie: zwycięstwo',
      u'Po bitwie: porażka', u'Misje osobiste', u'Legowisko pupila'),
  'de': (u'Garagenszenen', u'Szene', u'Standard', u'Anpassung',
      u'Fahrzeugübersicht', u'Panzerungsprüfung', u'Nach dem Gefecht: Sieg',
      u'Nach dem Gefecht: Niederlage', u'Persönliche Aufträge', u'Tierunterkunft'),
  'cs': (u'Scény garáže', u'Scéna', u'Výchozí', u'Úpravy',
      u'Přehled vozidla', u'Kontrola pancíře', u'Po bitvě: vítězství',
      u'Po bitvě: porážka', u'Osobní mise', u'Pelíšek'),
  'uk': (u'Сцени ангара', u'Сцена', u'Звичайний', u'Персоналізація',
      u'Огляд техніки', u'Огляд броні', u'Після бою: перемога',
      u'Після бою: поразка', u'Особисті завдання', u'Лігво улюбленця'),
  'fr': (u'Scènes du garage', u'Scène', u'Standard', u'Personnalisation',
      u'Vue du véhicule', u'Inspection du blindage', u'Après la bataille : victoire',
      u'Après la bataille : défaite', u'Missions personnelles', u'Repaire de l’animal'),
  'es': (u'Escenas del garaje', u'Escena', u'Normal', u'Personalización',
      u'Vista del vehículo', u'Inspección del blindaje', u'Tras la batalla: victoria',
      u'Tras la batalla: derrota', u'Misiones personales', u'Guarida de la mascota'),
  'it': (u'Scene dell’officina', u'Scena', u'Standard', u'Personalizzazione',
      u'Panoramica del veicolo', u'Ispezione corazzatura', u'Dopo la battaglia: vittoria',
      u'Dopo la battaglia: sconfitta', u'Missioni personali', u'Tana dell’animale'),
  'tr': (u'Garaj sahneleri', u'Sahne', u'Varsayılan', u'Özelleştirme',
      u'Araç görünümü', u'Zırh incelemesi', u'Savaş sonrası: zafer',
      u'Savaş sonrası: yenilgi', u'Kişisel görevler', u'Evcil hayvan yuvası'),
  'hu': (u'Garázsjelenetek', u'Jelenet', u'Alapértelmezett', u'Testreszabás',
      u'Járműáttekintés', u'Páncélvizsgálat', u'Csata után: győzelem',
      u'Csata után: vereség', u'Személyes küldetések', u'Kisállat kuckója'),
}

_LABELS = {
  'en': dict(
    title=u'Local map viewer', description=u'Explore maps with a free camera, without entering a battle. F8.',
    selectMap=u'Select map:', start=u'Start viewing', close=u'Close',
    panelTitle=u'VIEW SETTINGS', mouseHint=u'Ctrl — mouse control',
    back=u'BACK', toHangar=u'TO GARAGE', settings=u'Settings',
    resume=u'Return to viewing', exitToHangar=u'Exit to Garage'),
  'ru': dict(
    title=u'Локальный просмотр карт', description=u'Карты и свободная камера без создания боя. F8.',
    selectMap=u'Выбор карты:', start=u'Начать просмотр', close=u'Закрыть',
    panelTitle=u'ПАРАМЕТРЫ ПРОСМОТРА', mouseHint=u'Ctrl — управление мышью',
    back=u'НАЗАД', toHangar=u'В АНГАР', settings=u'Настройки',
    resume=u'Вернуться к просмотру', exitToHangar=u'Выйти в ангар'),
  'pl': dict(
    title=u'Lokalna przeglądarka map', description=u'Zwiedzaj mapy swobodną kamerą bez wchodzenia do bitwy. F8.',
    selectMap=u'Wybierz mapę:', start=u'Rozpocznij zwiedzanie', close=u'Zamknij',
    panelTitle=u'USTAWIENIA WIDOKU', mouseHint=u'Ctrl — sterowanie myszą',
    back=u'WRÓĆ', toHangar=u'DO GARAŻU', settings=u'Ustawienia',
    resume=u'Wróć do zwiedzania', exitToHangar=u'Wyjdź do garażu'),
  'de': dict(
    title=u'Lokale Kartenansicht', description=u'Karten mit freier Kamera ohne Gefecht erkunden. F8.',
    selectMap=u'Karte auswählen:', start=u'Ansicht starten', close=u'Schließen',
    panelTitle=u'ANSICHTSEINSTELLUNGEN', mouseHint=u'Strg — Maussteuerung',
    back=u'ZURÜCK', toHangar=u'ZUR GARAGE', settings=u'Einstellungen',
    resume=u'Zurück zur Kartenansicht', exitToHangar=u'Zur Garage'),
  'cs': dict(
    title=u'Místní prohlížeč map', description=u'Prohlížejte mapy volnou kamerou bez vstupu do bitvy. F8.',
    selectMap=u'Vyberte mapu:', start=u'Zahájit prohlížení', close=u'Zavřít',
    panelTitle=u'NASTAVENÍ ZOBRAZENÍ', mouseHint=u'Ctrl — ovládání myší',
    back=u'ZPĚT', toHangar=u'DO GARÁŽE', settings=u'Nastavení',
    resume=u'Zpět k prohlížení', exitToHangar=u'Odejít do garáže'),
  'uk': dict(
    title=u'Локальний перегляд мап', description=u'Мапи та вільна камера без входу в бій. F8.',
    selectMap=u'Вибір мапи:', start=u'Почати перегляд', close=u'Закрити',
    panelTitle=u'ПАРАМЕТРИ ПЕРЕГЛЯДУ', mouseHint=u'Ctrl — керування мишею',
    back=u'НАЗАД', toHangar=u'ДО ГАРАЖА', settings=u'Налаштування',
    resume=u'Повернутися до перегляду', exitToHangar=u'Вийти до гаража'),
  'fr': dict(
    title=u'Explorateur de cartes local', description=u'Explorez les cartes en caméra libre sans entrer en bataille. F8.',
    selectMap=u'Choisir une carte :', start=u'Commencer la visite', close=u'Fermer',
    panelTitle=u'PARAMÈTRES DE VUE', mouseHint=u'Ctrl — contrôle de la souris',
    back=u'RETOUR', toHangar=u'AU GARAGE', settings=u'Paramètres',
    resume=u'Reprendre la visite', exitToHangar=u'Quitter vers le garage'),
  'es': dict(
    title=u'Visor local de mapas', description=u'Explora mapas con cámara libre sin entrar en batalla. F8.',
    selectMap=u'Elige un mapa:', start=u'Iniciar exploración', close=u'Cerrar',
    panelTitle=u'AJUSTES DE VISTA', mouseHint=u'Ctrl — control del ratón',
    back=u'VOLVER', toHangar=u'AL GARAJE', settings=u'Ajustes',
    resume=u'Volver a la exploración', exitToHangar=u'Salir al garaje'),
  'it': dict(
    title=u'Visualizzatore locale di mappe', description=u'Esplora le mappe con la telecamera libera senza entrare in battaglia. F8.',
    selectMap=u'Seleziona una mappa:', start=u'Inizia esplorazione', close=u'Chiudi',
    panelTitle=u'IMPOSTAZIONI VISUALE', mouseHint=u'Ctrl — controllo del mouse',
    back=u'INDIETRO', toHangar=u'ALL’OFFICINA', settings=u'Impostazioni',
    resume=u'Torna all’esplorazione', exitToHangar=u'Esci e torna in Officina'),
  'tr': dict(
    title=u'Yerel harita görüntüleyici', description=u'Savaşa girmeden haritaları serbest kamerayla keşfedin. F8.',
    selectMap=u'Harita seçin:', start=u'Keşfe başla', close=u'Kapat',
    panelTitle=u'GÖRÜNÜM AYARLARI', mouseHint=u'Ctrl — fare kontrolü',
    back=u'GERİ', toHangar=u'GARAJA', settings=u'Ayarlar',
    resume=u'Keşfe dön', exitToHangar=u'Garaja dön'),
  'hu': dict(
    title=u'Helyi pályanézegető', description=u'Fedezd fel a pályákat szabad kamerával, csata nélkül. F8.',
    selectMap=u'Válassz pályát:', start=u'Felfedezés indítása', close=u'Bezárás',
    panelTitle=u'NÉZETBEÁLLÍTÁSOK', mouseHint=u'Ctrl — egérvezérlés',
    back=u'VISSZA', toHangar=u'A GARÁZSBA', settings=u'Beállítások',
    resume=u'Vissza a felfedezéshez', exitToHangar=u'Vissza a garázsba'),
}

def texts(language=None):
  if language is None:
    from helpers import getClientLanguage
    language = getClientLanguage()
  language = (language or '').lower().replace('_', '-').split('-')[0]
  result = dict(_LABELS.get(language, _LABELS['en']))
  loginLabels = {
    'ru': (u'НА ЭКРАН ВХОДА', u'Выйти на экран входа'),
    'en': (u'TO LOGIN SCREEN', u'Exit to login screen'),
  }
  result['toLogin'], result['exitToLogin'] = loginLabels.get(language, loginLabels['en'])
  result.update(zip(('dynamicEvents', 'dynamicEventName', 'eventPlay', 'eventPause'),
           _EVENT_LABELS.get(language, _EVENT_LABELS['en'])))
  result['hangar'] = _HANGAR_LABELS.get(language, _HANGAR_LABELS['en'])
  result.update(zip(('eventMode', 'waffentragerMode'),
           _MODE_LABELS.get(language, _MODE_LABELS['en'])))
  result.update(zip(_SCENE_KEYS, _SCENE_LABELS.get(language, _SCENE_LABELS['en'])))
  return result

def text(key):
  return texts()[key]
