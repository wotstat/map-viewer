# coding: utf-8
"""Viewer-owned text. Map names and external sections keep their own translations."""

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
    return dict(_LABELS.get(language, _LABELS['en']))


def text(key):
    return texts()[key]
