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
  totalAvatarSetsCount: {
    id: 'modules.avatars.total-avatars.counter.text',
    defaultMessage: 'Загальна кількість аватарів: {avatarSetsCount}',
    description: 'Текст, що відображає загальну кількість аватарів.',
  },
  addAvatarSetBtnText: {
    id: 'modules.avatars.button.add-avatar-set',
    defaultMessage: 'Додати набір аватарів',
    description: 'Текст, що відображається на кнопці додавання набору аватарів.',
  },
  alertEmptyAvatarSetListTitle: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.title',
    defaultMessage: 'Немає доступних аватарів',
    description: 'Заголовок сповіщення, коли немає надобу аватарів для відображення.',
  },
  alertEmptyAvatarSetListDescription: {
    id: 'modules.avatars.avatar-set.alert.empty-avatars-list.description',
    defaultMessage: 'Наразі відсутні набори аватарів для відображення.',
    description: 'Опис сповіщення, коли немає наборів аватарів для відображення.',
  },
  avatarSetEditBtnTitle: {
    id: 'modules.avatars.avatar-set.button.edit.title',
    defaultMessage: 'Редагувати',
    description: 'Текст, що відображається на кнопці редагування набору аватарів.',
  },
  avatarSetDeleteBtnTitle: {
    id: 'modules.avatars.avatar-set.button.delete.title',
    defaultMessage: 'Видалити',
    description: 'Текст, що відображається на кнопці видалення набору аватарів.',
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
  avatarSetStepperEvolutionStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.title',
    defaultMessage: 'Конфігурація',
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
  toastNewAvatarSetCreatedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.created.avatar-set.title',
    defaultMessage: 'Новий набір аватарів успішно створено',
    description: 'Заголовок для сповіщення, коли новий набір аватарів успішно створено.',
  },
  toastAvatarSetDeletedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.deleted.avatar-set.title',
    defaultMessage: 'Набір аватарів успішно видалено',
    description: 'Заголовок для сповіщення, коли набір аватарів успішно видалено.',
  },
});

export default messages;
