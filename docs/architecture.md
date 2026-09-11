# Архитектура

Мод загружает клиентскую геометрию без серверного боя и Avatar.
Python-код находится в `res/scripts/client/gui/mods/`, AS3 — в `as3/src/wotstat/localmaps/`.

## Основные модули

| Модуль | Ответственность |
|---|---|
| `mod_wotstat_local_maps.py`, `bootstrap.py` | Загрузка мода, F8, ModsList, окно выбора |
| `catalog.py`, `preview.py` | Карты и режимы из `ArenaType`, штатное превью |
| `viewer.py`, `cleanup.py` | Сессия просмотра, переходы и восстановление ангара |
| `flight.py` | Движение камеры, скорость и зум |
| `battle_app.py`, `ui_routing.py` | Локальное battle app, меню, настройки и маршрутизация окон |
| `loading.py`, `border.py`, `space_hooks.py` | Экран перехода, граница карты, адаптация UDO |
| `minimap_bounds.py`, `minimap_points.py` | Границы текстуры и точки выбранного режима |
| `native_library.py` | Загрузка кода штатных ангарных контролов в боевой movie |
| `debug_panel.py`, `events.py` | Публичные настройки и события для других модов |
| `MapBridge.as`, `MapSelector.as` | Мост ангарного UI и окно выбора карты |
| `BattleBridge.as`, `DebugPanel.as`, `DebugControl.as`, `DebugTooltip.as` | HUD и панель настроек |
| `NativeLobbyLibrary.as` | Подключение штатных библиотек контролов |

## Жизненный цикл

Каталог группирует `ArenaType.g_cache` по геометрии и оставляет режимы с установленным
`space.settings`. Маску видимости выбранного режима даёт `SpaceVisibilityFlagsFactory`.

`LocalSession` сохраняет Account, танк, окружение ангара, FOV и состояние ввода/UI.
После `HangarSpace.destroy()` создаёт собственное пространство и загружает геометрию
через `addSpaceGeometryMapping()`. Мир отображает `BigWorld.FreeCamera`.
`LoadingCover` использует независимый Flash root со штатным `WaitingTransition`,
который переживает смену приложений; таймаут прерывает незавершённый переход.

Готовность геометрии и HUD вызывает `ready`. Перед очисткой вызывается `stopping`:
внешние моды должны синхронно убрать модели и callbacks. `CleanupStack` выполняет
обратные действия, продолжая очистку при ошибке отдельного шага. Удаляется только
собственное пространство; `HangarSpace.init()` восстанавливает ангар. Новый вход
блокируется до готовности ангара и танка. `stopped` завершает цикл событий.
Контракт прерванной загрузки и поля контекста описаны в [API](debug-panel-api.md).

## UI и ввод

Селектор наследует `AbstractWindowView` и использует штатные `Window`, список,
dropdown и `MinimapLobby`. Боевой HUD работает в отдельном `battle.swf` через
`GUI.Flash` с менеджерами `BattleEntry`/`AppEntry`. Адаптер корня заменяет фабрику
`MainWindow` только в локальной копии функции: второй Wulf `MAIN_WINDOW`
конфликтует с областями основного окна. `BattleGameInputMgr` требует Avatar
и здесь не создаётся.

Миникарта, значки, меню Esc и настройки используют штатные компоненты.
Маршрутизация дочерних окон временно направляется в локальное battle app
и восстанавливается при выходе. Ангарный и боевой AS3-код разделены по movie.
Для ангарных контролов `native_library` извлекает из установленного `lobby.swf`
код без корневого `LobbyApplication` и загружает его в память через
`NativeLobbyLibrary`. Игровой код и библиотеки в пакет не включаются.

Ctrl включает `GUI_ENABLED` и отключает ввод камеры с плавным затуханием инерции.
Отпускание обоих Ctrl возвращает `CURSOR_ATTACHED`; курсор синхронизируется
через `CursorManager.resetMousePosition`. Меню и потеря фокуса останавливают
движение. Перед удалением контролов или отключением ввода фокус возвращается
на HUD, dropdown закрывается. M/V управляют видимостью миникарты и HUD;
новый просмотр сбрасывает эти флаги.

Реестр секций сохраняется между просмотрами; HUD отписывается от него при уничтожении.
Встроенных секций нет. Внешние интеграции, включая vegetation, используют
только [публичный API](debug-panel-api.md).

## Контракты для переноса на новый патч

Проверяй в исходниках клиента `wot-src-ru`, ветка `mt-ru`:

- `gui/ClientHangarSpace.py`, `gui/shared/utils/HangarSpace.py` — восстановление
  ангара, окружения и маски видимости; `helpers/OfflineMode.py` — пространство и камера.
- `gui/Scaleform/framework/application.py`, `battle_entry.py` — Flash root и DAAPI;
  `SettingsWindow.py`, `framework/package_layout.py` — меню и маршрутизация окон.
- `gui/Scaleform/daapi/view/battle/shared/minimap/component.py` — миникарта;
  `story_mode/gui/scaleform/daapi/view/battle/minimap.py` — квадратные границы
  текстуры прямоугольной карты. Граница мира остаётся исходным прямоугольником.
- `ArenaBorderController` / `ArenaBorderHelper` — граница с ID локального пространства.
- `SoundZoneTrigger.__init__` — создаёт CGF-объект в `player().spaceID`, который
  у Account равен 0. `space_hooks` использует локальную копию конструктора
  с CGF-фасадом, подставляющим ID просмотра; глобальный CGF не заменяется.

Сценарии регрессии: [проверка выпуска](release-checklist.md).
