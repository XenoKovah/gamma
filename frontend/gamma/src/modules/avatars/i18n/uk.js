import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.avatars.heading.text',
    defaultMessage: 'Налаштування аватарів',
    description: 'Текст, що відображається в заголовку сторінки налаштувань аватарів.',
  },
  pageDescription: {
    id: 'modules.avatars.page.description',
    defaultMessage: 'Ця сторінка відображає аватари та дозволяє користувачам створювати і редагувати їх.',
    description: 'Опис сторінки налаштувань аватарів.',
  },
  studentAvatarLockedTitle: {
    id: 'modules.avatars.student.avatar.locked.text',
    defaultMessage: 'Персонаж заблокований',
    description: 'Текст, що відображається на бейджі заблокованого аватара.',
  },
  totalAvatarSetsCount: {
    id: 'modules.avatars.total-avatars-sets.counter.text',
    defaultMessage: 'Загальна кількість наборів аватарів: {avatarSetsCount}',
    description: 'Текст, що відображає загальну кількість наборів аватарів.',
  },
  totalAvatarsCount: {
    id: 'modules.avatars.total-avatars.counter.text',
    defaultMessage: 'Загальна кількість аватарів: {avatarsCount}',
    description: 'Текст, що відображає загальну кількість аватарів.',
  },
  addAvatarSetBtnText: {
    id: 'modules.avatars.button.add-avatar-set',
    defaultMessage: 'Додати набір аватарів',
    description: 'Текст, що відображається на кнопці додавання набору аватарів.',
  },
  alertEmptyAvatarSetListTitle: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.title',
    defaultMessage: 'Немає доступних наборів аватарів',
    description: 'Заголовок сповіщення, коли немає наборів аватарів для відображення.',
  },
  alertEmptyAvatarsListTitle: {
    id: 'modules.avatars.avatars.alert.empty-avatars-list.title',
    defaultMessage: 'Немає доступних аватарів',
    description: 'Заголовок сповіщення, коли немає аватарів для відображення.',
  },
  alertEmptyAvatarSetListDescription: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.description',
    defaultMessage: 'Наразі відсутні набори аватарів для відображення.',
    description: 'Опис сповіщення, коли немає наборів аватарів для відображення.',
  },
  alertEmptyAvatarsListDescription: {
    id: 'modules.avatars.avatars.alert.empty-avatars-list.description',
    defaultMessage: 'Потрібно не менше двох стадій набору аватарів.',
    description: 'Опис сповіщення, коли немає аватарів для відображення.',
  },
  avatarSetEditBtnTitle: {
    id: 'modules.avatars.avatar-set.button.edit.title',
    defaultMessage: 'Редагувати',
    description: 'Текст, що відображається на кнопці редагування набору аватарів.',
  },
  avatarEditBtnTitle: {
    id: 'modules.avatars.avatar.button.edit.title',
    defaultMessage: 'Редагувати',
    description: 'Текст, що відображається на кнопці редагування аватару.',
  },
  avatarSetDeleteBtnTitle: {
    id: 'modules.avatars.avatar-set.button.delete.title',
    defaultMessage: 'Видалити',
    description: 'Текст, що відображається на кнопці видалення набору аватарів.',
  },
  avatarSetDraftBadgeText: {
    id: 'modules.avatars.avatar-set.draft.badge.text',
    defaultMessage: 'Чернетка',
    description: 'Текст, що відображається на значку набору аватарів зі статусом чернетки.',
  },
  avatarDeleteBtnTitle: {
    id: 'modules.avatars.avatar.button.delete.title',
    defaultMessage: 'Видалити',
    description: 'Текст, що відображається на кнопці видалення аватару',
  },
  toastErrorTitle: {
    id: 'modules.avatars.toast.error.text',
    defaultMessage: 'Сталася помилка.',
    description: 'Текст, що відображається в сповіщенні про помилку.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.avatars.alert.modal.confirm.deletion.title',
    defaultMessage: 'Підтвердження видалення',
    description: 'Заголовок модального вікна підтвердження видалення аватар сету.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.description',
    defaultMessage: 'Ви впевнені, що хочете видалити цей аватар сет? Цю дію неможливо скасувати.',
    description: 'Опис у модальному вікні підтвердження видалення аватар сету.',
  },
  avatarSetStepperBtnStatefulDefaultText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.default.text',
    defaultMessage: 'Далі',
    description: 'Текст для кнопки у її стандартному стані в майстрі створення набору аватарів.',
  },
  avatarSetStepperBtnStatefulPendingText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.pending.text',
    defaultMessage: 'Збереження',
    description: 'Текст для кнопки у стані очікування в майстрі створення набору аватарів.',
  },
  confirmAvatarDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.avatar.description',
    defaultMessage: 'Ви впевнені, що хочете видалити цей аватар? Цю дію неможливо скасувати.',
    description: 'Опис для модального вікна підтвердження видалення аватара.',
  },
  editAvatarModalTitle: {
    id: 'modules.avatars.manage.modal.edit-avatar.title',
    defaultMessage: 'Редагувати аватар',
    description: 'Заголовок модального вікна редагування аватара.',
  },
  avatarSetStepperBtnStatefulCompleteText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.complete.text',
    defaultMessage: 'Збережено',
    description: 'Текст для кнопки у завершеному стані в майстрі створення набору аватарів.',
  },
  avatarSetStepperBtnFinishText: {
    id: 'modules.avatars.avatar-set.stepper.button.finish.text',
    defaultMessage: 'Завершити',
    description: 'Текст для кнопки завершення в майстрі створення набору аватарів.',
  },
  avatarSetStepperTitle: {
    id: 'modules.avatars.avatar-set.stepper.add-avatar-set.title',
    defaultMessage: 'Додати новий набір аватарів',
    description: 'Заголовок майстра створення набору аватарів.',
  },
  avatarSetStepperValidationTitleRequired: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-required',
    defaultMessage: 'Назва є обов’язковою',
    description: 'Повідомлення про помилку для обов’язкового поля назви в майстрі створення набору аватарів.',
  },
  avatarSetStepperValidationTitleMaxLength: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-max-length',
    defaultMessage: 'Назва має містити не більше 50 символів',
    description: 'Повідомлення про помилку для обмеження довжини назви в майстрі створення набору аватарів.',
  },
  avatarSetStepperValidationTitleLettersNumbers: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-letters-numbers',
    defaultMessage: 'Назва має містити лише літери та цифри',
    description: 'Повідомлення про помилку для назви, яка має містити лише літери та цифри в майстрі створення набору аватарів.',
  },
  avatarSetStepperValidationTitleUnique: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-unique',
    defaultMessage: 'Така назва вже існує',
    description: 'Повідомлення про помилку для унікальності назви в майстрі створення набору аватарів.',
  },
  avatarSetStepperCloseBtnTitle: {
    id: 'modules.avatars.avatar-set.stepper.button.close.title',
    defaultMessage: 'Закрити',
    description: 'Заголовок для кнопки закриття в майстрі створення набору аватарів.',
  },
  avatarSetStepperAvatarsStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.avatars.title',
    defaultMessage: 'Аватари',
    description: 'Заголовок для кроку вибору аватарів у майстрі створення набору аватарів.',
  },
  avatarSetStepperFinishStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.finish.title',
    defaultMessage: 'Завершення',
    description: 'Заголовок для кроку завершення налаштування аватарів у майстрі створення набору аватарів.',
  },
  avatarCardRuleSectionTitle: {
    id: 'modules.avatars.avatar-set.card.rule.subsection.title',
    defaultMessage: 'Правило {count}',
    description: 'Заголовок підрозділу правил на картці аватару.',
  },
  avatarCardEventTypeFilterTitle: {
    id: 'modules.avatars.avatar-set.card.count.event-type.title',
    defaultMessage: 'Тип події',
    description: 'Заголовок для фільтру типу події на картці аватару.',
  },
  avatarCardCountFilterTitle: {
    id: 'modules.avatars.avatar-set.card.count.filter.title',
    defaultMessage: 'Кількість',
    description: 'Заголовок фільтру підрахунку на картці аватару.',
  },
  avatarCardIntervalFilterTitle: {
    id: 'modules.avatars.avatar-set.card.interval.filter.title',
    defaultMessage: 'Інтервал',
    description: 'Назва інтервального фільтру на картці аватару.',
  },
  avatarCardFrequencyFilterTitle: {
    id: 'modules.avatars.avatar-set.card.frequency.filter.title',
    defaultMessage: 'Частота',
    description: 'Назва фільтру частоти на картці аватару.',
  },
  avatarCardCourseFilterTitle: {
    id: 'modules.avatars.avatar-set.card.course.filter.title',
    defaultMessage: 'Курс',
    description: 'Назва для фільтру курсу на картці аватару.',
  },
  avatarCardOrganizationFilterTitle: {
    id: 'modules.avatars.avatar-set.card.organization.filter.title',
    defaultMessage: 'Організація',
    description: 'Заголовок фільтру організації на картці аватару.',
  },
  avatarSetStepperEvolutionStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.title',
    defaultMessage: 'Еволюція',
    description: 'Заголовок для кроку еволюції в майстрі створення набору аватарів.',
  },
  avatarSetStepperTitleStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.title.title',
    defaultMessage: 'Назва',
    description: 'Заголовок для кроку введення назви в майстрі створення набору аватарів.',
  },
  avatarSetStepperTitleStepDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.title.description',
    defaultMessage: 'Будь ласка, введіть назву набору аватарів нижче.',
    description: 'Опис для кроку введення назви в майстрі створення набору аватарів.',
  },
  avatarSetStepperTitleStepInputTitleLabel: {
    id: 'modules.avatars.avatar-set.stepper.step.title.input.title.label',
    defaultMessage: 'Введіть назву',
    description: 'Мітка для поля введення назви в кроці введення назви майстра створення набору аватарів.',
  },
  toastNewAvatarSetSavedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.saved.avatar-set.title',
    defaultMessage: 'Данні набору аватарів успішно збережені',
    description: 'Заголовок для сповіщення, коли новий набір аватарів успішно збережено.',
  },
  avatarSetStepperPreviousBtnTitle: {
    id: 'modules.avatars.avatar-set.stepper.button.previous.title',
    defaultMessage: 'Назад',
    description: 'Заголовок для кнопки "Назад" у покроковому майстрі створення аватар-сета.',
  },
  toastAvatarSetDeletedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.deleted.avatar-set.title',
    defaultMessage: 'Набір аватарів успішно видалено',
    description: 'Заголовок для сповіщення, коли набір аватарів успішно видалено.',
  },
  avatarSetStepperEvolutionAddStageBtn: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.button.add-stage.title',
    defaultMessage: 'Додати етап еволюції',
    description: 'Заголовок кнопки для додавання етапу еволюції на кроці еволюції в майстрі набору аватарів.',
  },
  avatarSetStepperEditTitle: {
    id: 'modules.avatars.avatar-set.stepper.edit-avatar-set.title',
    defaultMessage: 'Редагування набору аватарів',
    description: 'Заголовок майстра редагування набору аватарів.',
  },
  avatarSetStepperEvolutionDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.description.text',
    defaultMessage: `Будь ласка, завантажте базові файли для етапів еволюції аватара.
      Мінімальна кількість етапів еволюції – 2, максимальна – 5.
      Переконайтеся, що зображення не містять жодних аксесуарів. Підтримуваний формат файлів: SVG.
      Максимальний розмір файлу: 20 МБ.`,
    description: 'Опис для кроку еволюції в майстрі набору аватарів.',
  },
  avatarSetStepperEvolutionRemoveAvatarBtn: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.button.remove-avatar.text',
    defaultMessage: 'Видалити',
    description: 'Текст кнопки для видалення аватара на кроці еволюції в майстрі набору аватарів.',
  },
  avatarSetStepperEvolutionAvatarStageTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.stage.title',
    defaultMessage: 'Етап {index}',
    description: 'Заголовок для етапу аватара на кроці еволюції в майстрі набору аватарів.',
  },
  avatarSetStepperEvolutionAvatarDefaultTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.default.title',
    defaultMessage: 'Стандартний заголовок',
    description: 'Стандартний заголовок для аватара на кроці еволюції в майстрі набору аватарів.',
  },
  avatarSetStepperEvolutionAvatarDefaultDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.default.description',
    defaultMessage: 'Стандартний опис',
    description: 'Стандартний опис для аватара на кроці еволюції в майстрі набору аватарів.',
  },
});

export default messages;
