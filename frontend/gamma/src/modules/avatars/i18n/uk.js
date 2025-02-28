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
  addAvatarBtnText: {
    id: 'modules.avatars.button.add-avatar',
    defaultMessage: 'Додати аватар',
    description: 'Текст, що відображається на кнопці додавання аватара.',
  },
  alertEmptyAvatarsListTitle: {
    id: 'modules.avatars.alert.empty-avatars-list.title',
    defaultMessage: 'Немає доступних аватарів',
    description: 'Заголовок сповіщення, коли немає аватарів для відображення.',
  },
  alertEmptyAvatarsListDescription: {
    id: 'modules.avatars.alert.empty-avatars-list.description',
    defaultMessage: 'Наразі немає аватарів для відображення.',
    description: 'Опис сповіщення, коли немає аватарів для відображення.',
  },
  avatarEditBtnTitle: {
    id: 'modules.avatars.avatar-item.button.edit.title',
    defaultMessage: 'Редагувати',
    description: 'Текст, що відображається на кнопці редагування аватара.',
  },
  avatarDeleteBtnTitle: {
    id: 'modules.avatars.avatar-item.button.delete.title',
    defaultMessage: 'Видалити',
    description: 'Текст, що відображається на кнопці видалення аватара.',
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
  avatarStepperBtnStatefulDefaultText: {
    id: 'modules.avatars.stepper.button.stateful.default.text',
    defaultMessage: 'Далі',
    description: 'Текст для кнопки у її стандартному стані в майстрі створення аватарів.',
  },
  avatarStepperBtnStatefulPendingText: {
    id: 'modules.avatars.stepper.button.stateful.pending.text',
    defaultMessage: 'Збереження',
    description: 'Текст для кнопки у стані очікування в майстрі створення аватарів.',
  },
  avatarStepperBtnStatefulCompleteText: {
    id: 'modules.avatars.stepper.button.stateful.complete.text',
    defaultMessage: 'Збережено',
    description: 'Текст для кнопки у завершеному стані в майстрі створення аватарів.',
  },
  avatarStepperBtnFinishText: {
    id: 'modules.avatars.stepper.button.finish.text',
    defaultMessage: 'Завершити',
    description: 'Текст для кнопки завершення в майстрі створення аватарів.',
  },
  avatarStepperTitle: {
    id: 'modules.avatars.stepper.add-avatar-set.title',
    defaultMessage: 'Додати новий набір аватарів',
    description: 'Заголовок майстра створення аватарів.',
  },
  avatarStepperValidationTitleRequired: {
    id: 'modules.avatars.stepper.validation.title-required',
    defaultMessage: 'Назва є обов’язковою',
    description: 'Повідомлення про помилку для обов’язкового поля назви в майстрі створення аватарів.',
  },
  avatarStepperValidationTitleMaxLength: {
    id: 'modules.avatars.stepper.validation.title-max-length',
    defaultMessage: 'Назва має містити не більше 50 символів',
    description: 'Повідомлення про помилку для обмеження довжини назви в майстрі створення аватарів.',
  },
  avatarStepperValidationTitleLettersNumbers: {
    id: 'modules.avatars.stepper.validation.title-letters-numbers',
    defaultMessage: 'Назва має містити лише літери та цифри',
    description: 'Повідомлення про помилку для назви, яка має містити лише літери та цифри в майстрі створення аватарів.',
  },
  avatarStepperValidationTitleUnique: {
    id: 'modules.avatars.stepper.validation.title-unique',
    defaultMessage: 'Така назва вже існує',
    description: 'Повідомлення про помилку для унікальності назви в майстрі створення аватарів.',
  },
  avatarStepperCloseBtnTitle: {
    id: 'modules.avatars.stepper.button.close.title',
    defaultMessage: 'Закрити',
    description: 'Заголовок для кнопки закриття в майстрі створення аватарів.',
  },
  avatarStepperAvatarsStepTitle: {
    id: 'modules.avatars.stepper.step.avatars.title',
    defaultMessage: 'Аватари',
    description: 'Заголовок для кроку вибору аватарів у майстрі створення аватарів.',
  },
  avatarStepperConfigurationStepTitle: {
    id: 'modules.avatars.stepper.step.configuration.title',
    defaultMessage: 'Конфігурація',
    description: 'Заголовок для кроку конфігурації в майстрі створення аватарів.',
  },
  avatarStepperTitleStepTitle: {
    id: 'modules.avatars.stepper.step.title.title',
    defaultMessage: 'Назва',
    description: 'Заголовок для кроку введення назви в майстрі створення аватарів.',
  },
  avatarStepperTitleStepDescription: {
    id: 'modules.avatars.stepper.step.title.description',
    defaultMessage: 'Будь ласка, введіть назву набору аватарів нижче.',
    description: 'Опис для кроку введення назви в майстрі створення аватарів.',
  },
  avatarStepperTitleStepInputTitleLabel: {
    id: 'modules.avatars.stepper.step.title.input.title.label',
    defaultMessage: 'Введіть назву',
    description: 'Мітка для поля введення назви в кроці введення назви майстра створення аватарів.',
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
