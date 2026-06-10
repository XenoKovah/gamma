import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.badges.heading.text',
    defaultMessage: 'Configurações de conquistas',
    description: 'O texto exibido no cabeçalho da página de configurações de distintivos.',
  },
  pageDescription: {
    id: 'modules.badges.page.description',
    defaultMessage: 'Esta página exibe as conquistas e permite que os usuários as criem e editem.',
    description: 'A descrição da página de configurações de distintivos.',
  },
  addBadgeBtnText: {
    id: 'modules.badges.button.add-badge',
    defaultMessage: 'Adicionar conquista',
    description: 'O texto exibido no botão para adicionar um distintivo.',
  },
  totalBadgesCount: {
    id: 'modules.badges.total-badges.counter.text',
    defaultMessage: 'Total de conquistas: {badgesCount}',
    description: 'O texto exibido para o número total de distintivos.',
  },
  badgeEditBtnTitle: {
    id: 'modules.badges.badge-item.button.edit.title',
    defaultMessage: 'Editar',
    description: 'O texto exibido no botão para editar um distintivo.',
  },
  badgeDeleteBtnTitle: {
    id: 'modules.badges.badge-item.button.delete.title',
    defaultMessage: 'Excluir',
    description: 'O texto exibido no botão para excluir um distintivo.',
  },
  badgeDefaultTitle: {
    id: 'modules.badges.badge-item.default.title',
    defaultMessage: 'Título da conquista',
    description: 'O título padrão de um distintivo.',
  },
  badgeDefaultDescription: {
    id: 'modules.badges.badge-item.default.description',
    defaultMessage: 'Descrição da conquista',
    description: 'A descrição padrão de um distintivo.',
  },
  alertEmptyBadgesListTitle: {
    id: 'modules.badges.alert.empty-badges-list.title',
    defaultMessage: 'Nenhuma conquista disponível',
    description: 'O título do alerta quando não há distintivos para exibir.',
  },
  alertEmptyBadgesListDescription: {
    id: 'modules.badges.alert.empty-badges-list.description',
    defaultMessage: 'Atualmente, não há conquistas para exibir.',
    description: 'A descrição do alerta quando não há distintivos para exibir.',
  },
  addManageEntityModalTitle: {
    id: 'modules.badges.modal.add-badge.title',
    defaultMessage: 'Adicionar nova conquista',
    description: 'O título do modal para adicionar distintivo.',
  },
  editManageEntityModalTitle: {
    id: 'modules.badges.modal.edit-badge.title',
    defaultMessage: 'Editar conquista',
    description: 'O título do modal para editar distintivo.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.badges.alert.modal.confirm.deletion.title',
    defaultMessage: 'Confirmar exclusão',
    description: 'O título do modal de confirmação ao excluir um distintivo.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.badges.alert.modal.confirm.deletion.description',
    defaultMessage: 'Tem certeza de que deseja excluir esta conquista? Esta ação não pode ser desfeita.',
    description: 'A descrição do modal de confirmação ao excluir um distintivo.',
  },
  toastErrorTitle: {
    id: 'modules.badges.toast.error.text',
    defaultMessage: 'Ocorreu um erro.',
    description: 'O texto exibido na mensagem de erro do toast.',
  },
  badgeCreatedTitle: {
    id: 'modules.badges.alert.badge-created.title',
    defaultMessage: 'Conquista criada com sucesso',
    description: 'O título do alerta quando um distintivo é criado com sucesso.',
  },
  badgeEditedTitle: {
    id: 'modules.badges.alert.badge-edited.title',
    defaultMessage: 'Conquista editada com sucesso',
    description: 'O título do alerta quando um distintivo é editado com sucesso.',
  },
  badgeDeletedTitle: {
    id: 'modules.badges.alert.badge-deleted.title',
    defaultMessage: 'Conquista excluída com sucesso',
    description: 'O título do alerta quando um distintivo é excluído com sucesso.',
  },
  badgeDraftStatusText: {
    id: 'modules.badges.badge.draft.status.text',
    defaultMessage: 'Rascunho',
    description: 'O texto exibido para o status de rascunho do distintivo.',
  },
  badgeActiveStatusText: {
    id: 'modules.badges.badge.active.status.text',
    defaultMessage: 'Ativo',
    description: 'O texto exibido para o status ativo do distintivo.',
  },
});

export default messages;
