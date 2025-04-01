import { defineMessages } from 'react-intl';

const messages = defineMessages({
  loaderScreenReaderText: {
    id: 'generic.loader.screenReader.text',
    defaultMessage: 'Завантаження...',
    description: 'Текст для скрін-рідерів у компоненті Loader.',
  },
  alertDangerTitle: {
    id: 'generic.alert.danger.title',
    defaultMessage: 'Сталася помилка',
    description: 'Заголовок у компоненті сповіщення про помилку.',
  },
  alertDangerDescription: {
    id: 'generic.alert.danger.description',
    defaultMessage: 'Під час обробки вашого запиту сталася помилка. Будь ласка, спробуйте пізніше або зверніться до служби підтримки.',
    description: 'Опис у компоненті сповіщення про помилку.',
  },
  alertBtnCloseTitle: {
    id: 'generic.alert.button.close.title',
    defaultMessage: 'Закрити',
    description: 'Текст кнопки закриття у сповіщенні.',
  },
  modalDialogBtnCancelText: {
    id: 'generic.modal.dialog.button.cancel.text',
    defaultMessage: 'Скасувати',
    description: 'Текст кнопки скасування у модальному вікні.',
  },
  modalDialogBtnSubmitText: {
    id: 'generic.modal.dialog.button.submit.text',
    defaultMessage: 'Підтвердити',
    description: 'Текст кнопки підтвердження у модальному вікні.',
  },
  alertBtnCancelText: {
    id: 'generic.modal.alert.button.cancel.text',
    defaultMessage: 'Скасувати',
    description: 'Текст кнопки скасування у модальному попередження.',
  },
  alertBtnDeleteText: {
    id: 'generic.modal.alert.button.delete.text',
    defaultMessage: 'Видалити',
    description: 'Текст кнопки видалення у модальному попередження.',
  },
  headerBtnSingOutText: {
    id: 'generic.header.button.sing.out.text',
    defaultMessage: 'Вийти',
    description: 'Текст кнопки виходу у заголовку.',
  },
  headerLogoAltText: {
    id: 'generic.header.logo.alt.text',
    defaultMessage: 'Гейміфікація',
    description: 'Альтернативний текст для логотипу у заголовку.',
  },
  'generic.footer.logo.alt.text': {
    id: 'generic.footer.logo.alt.text',
    defaultMessage: 'Гейміфікація',
    description: 'Альтернативний текст для логотипу у підвалі сайту.',
  },
  btnStatefulDefaultText: {
    id: 'generic.modal.alert.button.stateful.default.text',
    defaultMessage: 'Видалити',
    description: 'Текст для кнопки стану за замовчуванням у модальному вікні попередження.',
  },
  btnStatefulPendingText: {
    id: 'generic.modal.alert.button.stateful.pending.text',
    defaultMessage: 'Видалення...',
    description: 'Текст для кнопки стану очікування у модальному попередження.',
  },
  btnStatefulCompleteText: {
    id: 'generic.modal.alert.button.stateful.complete.text',
    defaultMessage: 'Видалено',
    description: 'Текст для кнопки стану завершення у модальному попередження.',
  },
  btnStatefulErrorText: {
    id: 'generic.modal.alert.button.stateful.error.text',
    defaultMessage: 'Помилка',
    description: 'Текст для кнопки стану помилки у модальному попередження.',
  },
  modalDialogBtnStatefulDefaultText: {
    id: 'generic.modal.dialog.button.stateful.default.text',
    defaultMessage: 'Зберегти',
    description: 'Текст для кнопки стану за замовчуванням у модальному діалозі.',
  },
  modalDialogBtnStatefulPendingText: {
    id: 'generic.modal.dialog.button.stateful.pending.text',
    defaultMessage: 'Збереження...',
    description: 'Текст для кнопки стану очікування у модальному діалозі.',
  },
  modalDialogBtnStatefulCompleteText: {
    id: 'generic.modal.dialog.button.stateful.complete.text',
    defaultMessage: 'Збережено',
    description: 'Текст для кнопки стану завершення у модальному діалозі.',
  },
  modalDialogBtnStatefulErrorText: {
    id: 'generic.modal.dialog.button.stateful.error.text',
    defaultMessage: 'Помилка',
    description: 'Текст для кнопки стану помилки у модальному діалозі.',
  },
  modalEntityValidationTitleRequiredText: {
    id: 'generic.modal.entity.validation.title.required',
    defaultMessage: 'Назва є обов’язковою',
    description: 'Повідомлення про помилку, якщо назва не вказана.',
  },
  modalEntityValidationSlugRequiredText: {
    id: 'generic.modal.entity.validation.slug.required',
    defaultMessage: 'Мітка є обов’язковою',
    description: 'Повідомлення про помилку, якщо мітка не вказаний.',
  },
  modalEntityValidationSlugInvalidText: {
    id: 'generic.modal.entity.validation.slug.invalid',
    defaultMessage: 'Мітка може містити лише літери, цифри, підкреслення та дефіси',
    description: 'Повідомлення про помилку, якщо формат мітки неправильний.',
  },
  modalEntityValidationDescriptionRequiredText: {
    id: 'generic.modal.entity.validation.description.required',
    defaultMessage: 'Опис є обов’язковим',
    description: 'Повідомлення про помилку, якщо опис не вказаний.',
  },
  modalEntityValidationImageRequiredText: {
    id: 'generic.modal.entity.validation.image.required',
    defaultMessage: 'Зображення є обов’язковим',
    description: 'Повідомлення про помилку, якщо не завантажено зображення.',
  },
  modalEntityValidationImageSizeText: {
    id: 'generic.modal.entity.validation.image.size',
    defaultMessage: 'Розмір файлу має бути менше 2МБ',
    description: 'Повідомлення про помилку, якщо зображення перевищує обмеження за розміром файлу.',
  },
  modalEntityImageHeadingText: {
    id: 'generic.modal.entity.image.heading',
    defaultMessage: 'Зображення',
    description: 'Заголовок для розділу зображення у модальному вікні.',
  },
  modalEntityImageBtnUploadText: {
    id: 'generic.modal.entity.image.button.upload',
    defaultMessage: 'Завантажити зображення',
    description: 'Текст на кнопці завантаження зображення для об’єкта.',
  },
  modalEntityImagePreviewText: {
    id: 'generic.modal.entity.image.preview.screenReader.text',
    defaultMessage: 'Попередній перегляд зображення',
    description: 'Текст для скрін-рідерів у попередньому перегляді зображення.',
  },
  modalEntityInfoHeadingText: {
    id: 'generic.modal.entity.information.heading',
    defaultMessage: 'Загальна інформація',
    description: 'Заголовок для розділу загальної інформації у модальному вікні.',
  },
  modalEntityInfoLabelEntityTitle: {
    id: 'generic.modal.entity.information.label.entity.title',
    defaultMessage: 'Назва',
    description: 'Назви об’єкта у модальному вікні.',
  },
  modalEntityInfoLabelEntitySlugText: {
    id: 'generic.modal.entity.information.label.entity.slug',
    defaultMessage: 'Мітка',
    description: 'Мітка для об’єкта у модальному вікні.',
  },
  modalEntityInfoLabelEntityDescriptionText: {
    id: 'generic.modal.entity.information.label.entity.description',
    defaultMessage: 'Опис',
    description: 'Опис об’єкта у модальному вікні.',
  },
  modalEntityInfoLabelEntityIsActiveText: {
    id: 'generic.modal.entity.is-active.text',
    defaultMessage: 'Активний',
    description: 'Текст, що відображається для статусу активності значка.',
  },
  modalEntityRulesTitle: {
    id: 'generic.modal.entity.rules.heading',
    defaultMessage: 'Правила',
    description: 'Заголовок розділу правил в модальному вікні.',
  },
  modalEntityRulesAddNewRuleBtnText: {
    id: 'generic.modal.entity.rules.button.add-new-rule.text',
    defaultMessage: 'Додати нове правило',
    description: 'Текст кнопки для додавання нового правила.',
  },
  modalEntityRulesAlertNoRulesTitle: {
    id: 'generic.modal.entity.rules.alert.no-rules.heading',
    defaultMessage: 'Немає доступних правил',
    description: 'Заголовок для сповіщення, коли немає правил для відображення.',
  },
  modalEntityRulesAlertNoRulesDescription: {
    id: 'generic.modal.entity.rules.alert.no-rules.description',
    defaultMessage: 'Ви ще не додали жодного правила. Натисніть кнопку нижче, щоб додати перше правило.',
    description: 'Опис для сповіщення, коли немає правил для відображення.',
  },
  modalEntityRulesRuleTitle: {
    id: 'generic.modal.entity.rules.rule.heading',
    defaultMessage: 'Правило {id}',
    description: 'Заголовок для правила в модальному вікні.',
  },
  modalEntityRulesRuleEventTypeLabel: {
    id: 'generic.modal.entity.rules.rule.event-type.label',
    defaultMessage: 'Тип події',
    description: 'Назва типу події в модальному вікні.',
  },
  modalEntityRulesRuleCountLabel: {
    id: 'generic.modal.entity.rules.rule.count.label',
    defaultMessage: 'Кількість',
    description: 'Заголовок поля кількості в модальному вікні.',
  },
  modalEntityRulesRuleCourseLabel: {
    id: 'generic.modal.entity.rules.rule.course.label',
    defaultMessage: 'Курс',
    description: 'Заголовок для поля курсу в модальному вікні.',
  },
  modalEntityRulesBtnDeleteText: {
    id: 'generic.modal.entity.rules.button.delete.text',
    defaultMessage: 'Видалити правило',
    description: 'Текст на кнопці видалення правила.',
  },
  modalEntityRulesBtnRemoveFilterText: {
    id: 'generic.modal.entity.rules.button.remove-filter.text',
    defaultMessage: 'Видалити',
    description: 'Текст на кнопці видалення фільтра.',
  },
  modalEntityRulesIntervalStartLabelText: {
    id: 'generic.modal.entity.rules.interval.start.label.text',
    defaultMessage: 'Дата початку',
    description: 'Назва для інтервалу дати початку в модальному вікні.',
  },
  modalEntityRulesIntervalEndLabelText: {
    id: 'generic.modal.entity.rules.interval.end.label.text',
    defaultMessage: 'Дата завершення',
    description: 'Назва для інтервалу дати завершення в модальному вікні.',
  },
  modalEntityRulesActionHeadingTitle: {
    id: 'generic.modal.entity.rules.action.heading.text',
    defaultMessage: 'Дія',
    description: 'Заголовок для розділу дій в модальному вікні.',
  },
  modalEntityRulesFiltersHeadingTitle: {
    id: 'generic.modal.entity.rules.filters.heading.text',
    defaultMessage: 'Фільтри',
    description: 'Заголовок для розділу фільтрів в модальному вікні.',
  },
  modalEntityRulesFiltersSelectTitle: {
    id: 'generic.modal.entity.rules.filters.select.title',
    defaultMessage: 'Виберіть фільтр',
    description: 'Заголовок для випадаючого списку фільтрів в модальному вікні.',
  },
  modalEntityRulesFilterSelectTitle: {
    id: 'generic.modal.entity.rules.filter.select.title',
    defaultMessage: 'Виберіть {filterName}',
    description: 'Заголовок для випадаючого списку конкретного фільтра в модальному вікні.',
  },
  modalEntityActionEventNameLabelText: {
    id: 'generic.modal.entity.action.event.name.label',
    defaultMessage: 'Виберіть {eventType}',
    description: 'Назва для вибору типу події в модальному вікні.',
  },
  modalEntityValidationActionEventNameRequiredText: {
    id: 'generic.modal.entity.action.event.name.validation.text',
    defaultMessage: 'Тип події є обов’язковим',
    description: 'Повідомлення про помилку, якщо тип події не вказано.',
  },
  modalEntityValidationActionCountRequiredText: {
    id: 'generic.modal.entity.action.count.validation.required.text',
    defaultMessage: 'Кількість є обов’язковою',
    description: 'Повідомлення про помилку, якщо кількість не вказана.',
  },
  modalEntityValidationActionCountPositiveNumberText: {
    id: 'generic.modal.entity.action.count.validation.positive-number.text',
    defaultMessage: 'Кількість повинна бути додатним числом',
    description: 'Повідомлення про помилку, якщо кількість не є додатним числом.',
  },
  modalEntityValidationActionCountNumberText: {
    id: 'generic.modal.entity.action.count.validation.int.text',
    defaultMessage: 'Кількість повинна бути цілим числом',
    description: 'Повідомлення про помилку, якщо кількість не є цілим числом.',
  },
  modalEntityValidationStartDateRequiredText: {
    id: 'generic.modal.entity.interval.validation.start-date.required.text',
    defaultMessage: 'Дата початку є обов’язковою',
    description: 'Повідомлення про помилку, якщо дата початку не вказана.',
  },
  modalEntityValidationEndDateRequiredText: {
    id: 'generic.modal.entity.interval.validation.end-date.required.text',
    defaultMessage: 'Дата завершення є обов’язковою',
    description: 'Повідомлення про помилку, якщо дата завершення не вказана.',
  },
  modalEntityValidationFrequencyNumberText: {
    id: 'generic.modal.entity.frequency.validation.int.text',
    defaultMessage: 'Частота повинна бути числом',
    description: 'Повідомлення про помилку, якщо частота не є числом.',
  },
  modalEntityValidationFrequencyPositiveNumberText: {
    id: 'generic.modal.entity.frequency.validation.positive-int.text',
    defaultMessage: 'Частота повинна бути додатним числом',
    description: 'Повідомлення про помилку, якщо частота не є додатним числом.',
  },
  modalEntityValidationFiltersText: {
    id: 'generic.modal.entity.filters.validation.text',
    defaultMessage: 'є обов’язковим',
    description: 'Повідомлення про помилку, якщо фільтр відсутній.',
  },
  modalEntityOrganizationFilterTitle: {
    id: 'generic.modal.entity.organization.filter.title',
    defaultMessage: 'Організація',
    description: 'Заголовок для фільтра організації в модальному вікні.',
  },
  modalEntityValidationTitleMaxLengthText: {
    id: 'generic.modal.entity.validation.title.max-length',
    defaultMessage: 'Назва не повинна перевищувати 100 символів.',
    description: 'Повідомлення про помилку, якщо назва перевищує максимальну довжину.',
  },
  modalEntityValidationSlugMaxLengthText: {
    id: 'generic.modal.entity.validation.slug.max-length',
    defaultMessage: 'Мітка не повинна перевищувати 30 символів.',
    description: 'Повідомлення про помилку, якщо мітка перевищує максимальну довжину.',
  },
  modalEntityValidationDescriptionMaxLengthText: {
    id: 'generic.modal.entity.validation.description.max-length',
    defaultMessage: 'Опис не повинен перевищувати 300 символів.',
    description: 'Повідомлення про помилку, якщо опис перевищує максимальну довжину.',
  },
  headerBadgesLinkText: {
    id: 'generic.header.nav.badges',
    defaultMessage: 'Значки',
    description: 'Текст для посилання на значки в заголовку.',
  },
  headerAvatarsLinkText: {
    id: 'generic.header.nav.avatars',
    defaultMessage: 'Аватар',
    description: 'Текст для посилання на аватар у заголовку.',
  },
  pgnToastCloseLabel: {
    id: 'pgn.Toast.closeLabel',
    defaultMessage: 'Закрити',
    description: 'Текст для закриття сповіщення.',
  },
  pgnDropzonefileTypeRestriction: {
    id: 'pgn.Dropzone.DefaultContent.fileTypeRestriction',
    defaultMessage: 'Завантажуйте {count, plural, one {{firstPart} файл} other {{firstPart} або {secondPart} файли}}',
    description: 'Текст для обмеження типу файлів у компоненті Dropzone.',
  },
  pgnDropzonefileSizeMax: {
    id: 'pgn.Dropzone.DefaultContent.fileSizeMax',
    defaultMessage: 'Максимум {sizeMax}',
    description: 'Текст для максимального розміру файлу у компоненті Dropzone.',
  },
  pgnDropzoneDefaultContentLabel: {
    id: 'pgn.Dropzone.DefaultContent.label',
    defaultMessage: 'Перетягніть файл сюди або натисніть, щоб завантажити.',
    description: 'Текст, який відображається як мітка для введення компонента Dropzone.',
  },
  invalidSizeMore: {
    id: 'dropzone.Dropzone.invalidSizeMoreError',
    defaultMessage: 'Файл повинен бути меншим за {size}.',
    description: 'Повідомлення, що відображається при спробі завантажити файл, який перевищує максимально дозволений розмір у Dropzone.',
  },
  genericManageEntityModalEntityInfoTitle: {
    id: 'generic.manage.entity.modal.entity.info.title',
    defaultMessage: 'Заголовок повинен містити лише літери та цифри',
    description: 'Повідомлення про валідацію для поля заголовка в модальному вікні керування сутністю.',
  },
});

export default messages;
