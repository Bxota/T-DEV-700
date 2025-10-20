import React, { useState, useEffect } from 'react';
import './Horaires.css';
import { getAuthHeaders } from '../../api/auth';

const Horaires = () => {
  const [horaires, setHoraires] = useState([]);
  const [rules, setRules] = useState([]); // Nouvel état pour les règles
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [users, setUsers] = useState([]);
  
  const [viewingHoraire, setViewingHoraire] = useState(null);
  const [editingHoraire, setEditingHoraire] = useState(null);
  const [deletingHoraire, setDeletingHoraire] = useState(null);
  const [addingHoraire, setAddingHoraire] = useState(false);
  
  // Nouveaux états pour les règles
  const [viewingRule, setViewingRule] = useState(null);
  const [editingRule, setEditingRule] = useState(null);
  const [deletingRule, setDeletingRule] = useState(null);
  const [addingRule, setAddingRule] = useState(false);
  
  // Nouveaux états pour les exceptions
  const [exceptions, setExceptions] = useState([]);
  const [loadingExceptions, setLoadingExceptions] = useState(false);
  const [viewingException, setViewingException] = useState(null);
  const [editingException, setEditingException] = useState(null);
  const [deletingException, setDeletingException] = useState(null);
  const [addingException, setAddingException] = useState(false);
  
  // AJOUTER CETTE LIGNE - définir selectedRule pour les exceptions
  const [selectedRule, setSelectedRule] = useState('');
  
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(() => {
    const storedUser = localStorage.getItem('user');
    return storedUser ? JSON.parse(storedUser) : null;
  });
  
  const [newHoraireData, setNewHoraireData] = useState({
    name: '',
    default_duration_minutes: 480,
    timezone: 'Europe/Paris',
    role_id: null,
    is_active: true
  });
  
  // Nouvel état pour les données de règle
  const [newRuleData, setNewRuleData] = useState({
    weekday: 1,
    start_local_time: '',
    duration_minutes: 480,
    effective_from: new Date().toISOString().split('T')[0],
    effective_to: new Date().toISOString().split('T')[0],
    apply_to_whole_team: false,
    assigned_user_ids: []
  });
  
  // État pour les données d'exception
  const [newExceptionData, setNewExceptionData] = useState({
    date: new Date().toISOString().split('T')[0],
    is_skipped: false,
    override_start_local_time: '',
    override_duration_minutes: 480,
    note: ''
  });
  
  const [errorModal, setErrorModal] = useState({ show: false, message: '', title: '' });

  // ÉTAT POUR LA GÉNÉRATION (pas de sélection de template)
  const [generatingTemplate, setGeneratingTemplate] = useState(false);
  const [numberOfDays, setNumberOfDays] = useState(7);

  // Jours de la semaine
  const weekdays = [
    { id: 0, name: 'Lundi' },
    { id: 1, name: 'Mardi' },
    { id: 2, name: 'Mercredi' },
    { id: 3, name: 'Jeudi' },
    { id: 4, name: 'Vendredi' },
    { id: 5, name: 'Samedi' },
    { id: 6, name: 'Dimanche' }
  ];

  const getWeekdayName = (weekdayId) => {
    const weekday = weekdays.find(w => w.id === weekdayId);
    return weekday ? weekday.name : 'Non défini';
  };

  // Récupération des données depuis l'API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        console.log('Utilisateur courant:', currentUser?.team?.id);
        
        if (!currentUser?.team?.id) {
          throw new Error('Utilisateur non assigné à une équipe');
        }
        
        let templatesList = [];
        
        // Récupération des templates
        const templatesResponse = await fetch(`/api/teams/${currentUser.team.id}/shift-templates/list`, {
          headers: getAuthHeaders()
        });
        
        if (templatesResponse.ok) {
          const templatesData = await templatesResponse.json();
          // console.log('Données templates reçues:', templatesData);
          
          templatesList = Array.isArray(templatesData) ? templatesData : 
                         Array.isArray(templatesData.results) ? templatesData.results : 
                         Array.isArray(templatesData.templates) ? templatesData.templates : [];
          
          setTemplates(templatesList);
        }

        // Récupération des utilisateurs
        const usersResponse = await fetch('/api/users/', {
          headers: getAuthHeaders()
        });
        
        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          const usersList = Array.isArray(usersData) ? usersData : 
                           Array.isArray(usersData.users) ? usersData.users : [];
          setUsers(usersList);
        }

        // Récupération des règles pour tous les templates
        let allRules = [];
        
        if (templatesList.length > 0) {
          for (const template of templatesList) {
            try {
              const rulesResponse = await fetch(`/api/shift-templates/${template.id}/rules/list`, {
                headers: getAuthHeaders()
              });
              
              if (rulesResponse.ok) {
                const rulesData = await rulesResponse.json();
                
                // Extraire les règles depuis results (comme pour les templates)
                const rulesList = Array.isArray(rulesData) ? rulesData : 
                                 Array.isArray(rulesData.results) ? rulesData.results : 
                                 Array.isArray(rulesData.rules) ? rulesData.rules : [];
                
                
                if (rulesList.length > 0) {
                  const rulesWithTemplate = rulesList.map(rule => ({
                    ...rule,
                    template_name: template.name,
                    template_id: template.id
                  }));
                  
                  allRules = [...allRules, ...rulesWithTemplate];
                } else {
                  console.log(`Aucune règle trouvée pour le template ${template.name} (ID: ${template.id})`);
                }
              } else {
                console.warn(`Erreur lors de la récupération des règles pour le template ${template.id}:`, rulesResponse.status);
              }
            } catch (err) {
              console.error(`Erreur lors de la récupération des règles pour le template ${template.id}:`, err);
            }
          }
        }
        
        setRules(allRules);
        console.log('Total des règles récupérées:', allRules.length);
        console.log('Règles finales:', allRules);
        
      } catch (err) {
        console.error('Erreur lors de la récupération des données:', err);
        setError(err.message);
        setTemplates([]);
        setRules([]);
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchData();
    } else {
      setLoading(false);
      setError('Utilisateur non connecté');
    }
  }, [currentUser]);

  useEffect(() => {
    // Forcer le format 24h au niveau du document
    document.documentElement.setAttribute('lang', 'fr-FR');
    
    // Forcer le format 24h pour les inputs time
    const timeInputs = document.querySelectorAll('input[type="time"]');
    timeInputs.forEach(input => {
      input.setAttribute('data-format', '24h');
    });
  }, []);

  const openAddHoraire = () => {
    setAddingHoraire(true);
    setNewHoraireData({
      name: '',
      default_duration_minutes: 480,
      timezone: 'Europe/Paris',
      role_id: null,
      is_active: true
    });
    setSelectedTemplate('');
    setSelectedUsers([]);
  };

  const closeAddHoraire = () => {
    setAddingHoraire(false);
    setNewHoraireData({
      name: '',
      default_duration_minutes: 480,
      timezone: 'Europe/Paris',
      role_id: null,
      is_active: true
    });
    setSelectedTemplate('');
    setSelectedUsers([]);
  };

  // Fonction pour afficher la modal d'erreur
  const showErrorModal = (title, message) => {
    setErrorModal({ show: true, title, message });
  };

  const closeErrorModal = () => {
    setErrorModal({ show: false, message: '', title: '' });
  };

  const handleAddHoraire = async () => {
    // Validation des champs obligatoires
    if (!newHoraireData.name.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un nom pour le template');
      return;
    }
    if (!newHoraireData.default_duration_minutes || newHoraireData.default_duration_minutes <= 0) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une durée valide');
      return;
    }
    if (!newHoraireData.timezone) {
      showErrorModal('Erreur de validation', 'Veuillez sélectionner un fuseau horaire');
      return;
    }
    
    try {
      // Préparer les données
      const payload = {
        name: newHoraireData.name.trim(),
        default_duration_minutes: parseInt(newHoraireData.default_duration_minutes),
        timezone: newHoraireData.timezone,
        role_id: newHoraireData.role_id ? parseInt(newHoraireData.role_id) : null,
        is_active: newHoraireData.is_active
      };
      
      console.log('Création template - Données envoyées:', payload);

      const response = await fetch(`/api/teams/${currentUser.team.id}/shift-templates`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Nouveau template créé:', responseData);
        
        const newTemplate = responseData.template || responseData;
        setTemplates(prev => [...prev, newTemplate]);
        closeAddHoraire();
      } else {
        let errorMessage = 'Erreur lors de la création du template';
        try {
          const errorData = await response.json();
          console.log('Erreur API:', errorData);
          errorMessage = errorData.message || errorData.error || errorData.detail || 
                        (errorData.non_field_errors && errorData.non_field_errors[0]) ||
                        errorMessage;
        } catch {
          const errorText = await response.text();
          console.log('Erreur texte:', errorText);
          errorMessage = errorText || errorMessage;
        }
        
        showErrorModal('Erreur de création', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  const openView = (horaire) => setViewingHoraire(horaire);
  const closeView = () => setViewingHoraire(null);

  const openEdit = (horaire) => {
    setEditingHoraire({ ...horaire });
    setSelectedTemplate(horaire.template_id?.toString() || '');
    setSelectedUsers(horaire.assigned_user_ids || []);
  };
  const closeEdit = () => {
    setEditingHoraire(null);
    setSelectedTemplate('');
    setSelectedUsers([]);
  };

  const handleSave = async () => {
    // Validation des champs obligatoires
    if (!editingHoraire.name.trim()) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un nom pour le template');
      return;
    }
    if (!editingHoraire.default_duration_minutes || editingHoraire.default_duration_minutes <= 0) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une durée valide');
      return;
    }

    try {
      const payload = {
        name: editingHoraire.name.trim(),
        default_duration_minutes: parseInt(editingHoraire.default_duration_minutes),
        timezone: editingHoraire.timezone,
        role_id: editingHoraire.role_id ? parseInt(editingHoraire.role_id) : null,
        is_active: editingHoraire.is_active
      };
      
      console.log('Modification template - Données envoyées:', payload);
      
      const response = await fetch(`/api/teams/${currentUser.team.id}/shift-templates/${editingHoraire.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Réponse de l\'API:', responseData);

        const updatedTemplate = responseData.template || responseData;

        setTemplates(prev => prev.map(template => 
          template.id === editingHoraire.id ? updatedTemplate : template
        ));

        if (viewingHoraire?.id === editingHoraire.id) {
          setViewingHoraire(updatedTemplate);
        }

        closeEdit();
      } else {
        let errorMessage = 'Erreur lors de la modification du template';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        
        showErrorModal('Erreur de modification', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  const askDelete = (horaire) => setDeletingHoraire(horaire);
  const cancelDelete = () => setDeletingHoraire(null);
  
  const confirmDelete = async () => {
    try {
      const response = await fetch(`/api/teams/${currentUser.team.id}/shift-templates/${deletingHoraire.id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        setTemplates(prev => prev.filter(t => t.id !== deletingHoraire.id));
        if (viewingHoraire?.id === deletingHoraire.id) setViewingHoraire(null);
        if (editingHoraire?.id === deletingHoraire.id) setEditingHoraire(null);
        setDeletingHoraire(null);
      } else {
        let errorMessage = 'Erreur lors de la suppression du template';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        }
        
        setDeletingHoraire(null);
        showErrorModal('Erreur de suppression', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      setDeletingHoraire(null);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  // Nouvelles fonctions pour les règles
  const openAddRule = () => {
    setAddingRule(true);
    setNewRuleData({
      weekday: 0,
      start_local_time: '',
      duration_minutes: 480,
      effective_from: new Date().toISOString().split('T')[0],
      effective_to: new Date().toISOString().split('T')[0],
      apply_to_whole_team: false,
      assigned_user_ids: []
    });
    setSelectedTemplate('');
    setSelectedUsers([]);
  };

  const closeAddRule = () => {
    setAddingRule(false);
    setSelectedTemplate('');
    setSelectedUsers([]);
  };

  const handleAddRule = async () => {
    if (!selectedTemplate) {
      showErrorModal('Erreur de validation', 'Veuillez sélectionner un template');
      return;
    }
    if (!newRuleData.start_local_time) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une heure de début');
      return;
    }
    if (!newRuleData.apply_to_whole_team && selectedUsers.length === 0) {
      showErrorModal('Erreur de validation', 'Veuillez sélectionner des utilisateurs ou appliquer à toute l\'équipe');
      return;
    }
    
    try {
      const payload = {
        ...newRuleData,
        // Convertir l'heure HH:MM en format HH:MM:SS.sssZ
        start_local_time: `${newRuleData.start_local_time}:${new Date().toISOString().substr(17)}`,
        assigned_user_ids: newRuleData.apply_to_whole_team ? [] : selectedUsers.map(id => parseInt(id))
      };
      
      console.log('Création règle - Données envoyées:', payload);
      
      const response = await fetch(`/api/shift-templates/${selectedTemplate}/rules`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        const templateInfo = templates.find(t => t.id === parseInt(selectedTemplate));
        const newRule = {
          ...(responseData.rule || responseData),
          template_name: templateInfo?.name,
          template_id: templateInfo?.id
        };
        
        setRules(prev => [...prev, newRule]);
        closeAddRule();
      } else {
        const errorData = await response.json();
        showErrorModal('Erreur de création', errorData.message || 'Erreur lors de la création de la règle');
      }
    } catch (err) {
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur');
    }
  };

  const openViewRule = (rule) => setViewingRule(rule);
  const closeViewRule = () => setViewingRule(null);

  const openEditRule = (rule) => {
    setEditingRule({ ...rule });
    setSelectedTemplate(rule.template_id?.toString() || '');
    setSelectedUsers(rule.assigned_user_ids || []);
  };
  
  const closeEditRule = () => {
    setEditingRule(null);
    setSelectedTemplate('');
    setSelectedUsers([]);
  };

  const askDeleteRule = (rule) => setDeletingRule(rule);
  const cancelDeleteRule = () => setDeletingRule(null);
  
  const confirmDeleteRule = async () => {
    try {
      const response = await fetch(`/api/shift-templates/${deletingRule.template_id}/rules/${deletingRule.id}/`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        setRules(prev => prev.filter(r => r.id !== deletingRule.id));
        if (viewingRule?.id === deletingRule.id) setViewingRule(null);
        if (editingRule?.id === deletingRule.id) setEditingRule(null);
        setDeletingRule(null);
      }
    } catch (err) {
      showErrorModal('Erreur réseau', 'Impossible de supprimer la règle');
    }
  };

  const handleSaveRule = async () => {
    // Validation des champs obligatoires
    if (!editingRule.start_local_time) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une heure de début');
      return;
    }
    if (!editingRule.duration_minutes || editingRule.duration_minutes <= 0) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une durée valide');
      return;
    }
    if (!editingRule.effective_from) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une date de début');
      return;
    }
    if (!editingRule.effective_to) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une date de fin');
      return;
    }
    if (editingRule.effective_from > editingRule.effective_to) {
      showErrorModal('Erreur de validation', 'La date de fin doit être après la date de début');
      return;
    }
    if (!editingRule.apply_to_whole_team && selectedUsers.length === 0) {
      showErrorModal('Erreur de validation', 'Veuillez sélectionner des utilisateurs ou appliquer à toute l\'équipe');
      return;
    }

    try {
      // Préparer le start_local_time
      let formattedStartTime;
      if (typeof editingRule.start_local_time === 'string' && editingRule.start_local_time.includes(':')) {
        // Si c'est au format HH:MM (venant de l'input time)
        formattedStartTime = `${editingRule.start_local_time}:${new Date().toISOString().substr(17)}`;
      } else {
        // Si c'est déjà au format ISO, on le garde tel quel
        formattedStartTime = editingRule.start_local_time;
      }

      const payload = {
        weekday: editingRule.weekday,
        start_local_time: formattedStartTime,
        duration_minutes: parseInt(editingRule.duration_minutes),
        effective_from: editingRule.effective_from,
        effective_to: editingRule.effective_to,
        apply_to_whole_team: editingRule.apply_to_whole_team,
        assigned_user_ids: editingRule.apply_to_whole_team ? [] : selectedUsers.map(id => parseInt(id))
      };
      
      console.log('Modification règle - Données envoyées:', payload);
      
      const response = await fetch(`/api/shift-templates/${editingRule.template_id}/rules/${editingRule.id}/`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Réponse de l\'API:', responseData);

        const updatedRule = responseData.rule || responseData;

        setRules(prev => prev.map(rule => 
          rule.id === editingRule.id ? { 
            ...updatedRule, 
            template_name: editingRule.template_name, 
            template_id: editingRule.template_id 
          } : rule
        ));

        if (viewingRule?.id === editingRule.id) {
          setViewingRule({ 
            ...updatedRule, 
            template_name: editingHoraire.template_name, 
            template_id: editingHoraire.template_id 
          });
        }

        closeEditRule();
      } else {
        let errorMessage = 'Erreur lors de la modification de la règle';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();  
          errorMessage = errorText || errorMessage;
        }
        
        showErrorModal('Erreur de modification', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  // Fonction pour ouvrir la modal de génération de template
  const generateTemplate = () => {
    setGeneratingTemplate(true);
    setNumberOfDays(7); // 7 jours par défaut
  };

  // Fonction pour fermer la modal de génération
  const closeGenerateTemplate = () => {
    setGeneratingTemplate(false);
  };

  // Fonction pour générer le template
  const handleGenerateTemplate = async () => {
    // Validation
    if (!numberOfDays || numberOfDays <= 0) {
      showErrorModal('Erreur de validation', 'Veuillez saisir un nombre de jours valide');
      return;
    }
    if (numberOfDays > 365) {
      showErrorModal('Erreur de validation', 'Le nombre de jours ne peut pas dépasser 365');
      return;
    }

    try {
      console.log('Génération planning - Données envoyées:', {
        days: numberOfDays
      });

      const response = await fetch(`/api/teams/${currentUser.team.id}/shifts/generate?days=${numberOfDays}`, {
        method: 'POST',
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Planning généré avec succès:', responseData);
        
        // Calculer les dates pour l'affichage
        const startDate = new Date().toLocaleDateString('fr-FR');
        const endDate = new Date(Date.now() + (numberOfDays - 1) * 24 * 60 * 60 * 1000).toLocaleDateString('fr-FR');
        
        // Afficher un message de succès avec les dates calculées
        showErrorModal('Succès', `Planning généré avec succès pour ${numberOfDays} jour(s) à partir d'aujourd'hui (du ${startDate} au ${endDate})`);
        
        closeGenerateTemplate();
        
        // Optionnel : recharger les données pour voir les nouveaux shifts créés
        // window.location.reload();
      } else {
        let errorMessage = 'Erreur lors de la génération du planning';
        try {
          const errorData = await response.json();
          console.log('Erreur API:', errorData);
          errorMessage = errorData.message || errorData.error || errorData.detail || 
                        (errorData.non_field_errors && errorData.non_field_errors[0]) ||
                        errorMessage;
        } catch {
          const errorText = await response.text();
          console.log('Erreur texte:', errorText);
          errorMessage = errorText || errorMessage;
        }
        
        showErrorModal('Erreur de génération', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  // Fonction pour formater l'heure depuis ISO string - MISE À JOUR
  const formatTime = (timeString) => {
    if (!timeString) return 'Non défini';
    try {
      // Si c'est au format HH:MM:SS.sssZ, extraire juste HH:MM
      if (timeString.includes(':') && timeString.length > 5) {
        return timeString.substring(0, 5); // Prendre les 5 premiers caractères (HH:MM)
      }
      // Si c'est une date ISO complète
      if (timeString.includes('T')) {
        const date = new Date(timeString);
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
      }
      // Sinon retourner tel quel
      return timeString.substring(0, 5);
    } catch {
      return 'Format invalide';
    }
  };

  // Fonction pour convertir time en input time format - MISE À JOUR
  const isoToTimeInput = (timeString) => {
    if (!timeString) return '';
    try {
      // Si c'est au format HH:MM:SS.sssZ, extraire juste HH:MM
      if (timeString.includes(':') && !timeString.includes('T')) {
        return timeString.substring(0, 5); // HH:MM
      }
      // Si c'est une date ISO complète
      if (timeString.includes('T')) {
        const date = new Date(timeString);
        return date.toTimeString().slice(0, 5); // HH:MM
      }
      return timeString.substring(0, 5);
    } catch {
      return '';
    }
  };

  // Fonction pour formater la durée
  const formatDuration = (minutes) => {
    if (!minutes) return 'Non défini';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h${mins > 0 ? ` ${mins}min` : ''}`;
  };

  // Fonction pour gérer la sélection multiple d'utilisateurs
  const handleUserSelection = (userId) => {
    setSelectedUsers(prev => {
      if (prev.includes(userId)) {
        return prev.filter(id => id !== userId);
      } else {
        return [...prev, userId];
      }
    });
  };

  const [activeTab, setActiveTab] = useState('templates'); // 'templates', 'rules', ou 'exceptions'

  // Fonction pour récupérer les exceptions d'une règle - CORRIGÉE
  const fetchExceptions = async (ruleId) => {
    if (!ruleId) {
      setExceptions([]);
      return;
    }

    setLoadingExceptions(true);
    try {
      // UTILISER LA BONNE ROUTE POUR LES EXCEPTIONS
      const response = await fetch(`/api/shift-rules/${ruleId}`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const exceptionsData = await response.json();
        console.log('Données d\'exceptions reçues:', exceptionsData);
        
        // Gérer différents formats de réponse possibles
        const exceptionsList = Array.isArray(exceptionsData) ? exceptionsData : 
                              Array.isArray(exceptionsData.results) ? exceptionsData.results : 
                              Array.isArray(exceptionsData.exceptions) ? exceptionsData.exceptions : 
                              [];
        
        // Ajouter les informations de la règle à chaque exception
        const ruleInfo = rules.find(r => r.id === parseInt(ruleId));
        const exceptionsWithRule = exceptionsList.map(exception => ({
          ...exception,
          rule_name: ruleInfo?.template_name || 'Règle inconnue',
          rule_id: ruleInfo?.id
        }));
        
        setExceptions(exceptionsWithRule);
        console.log('Exceptions récupérées pour la règle', ruleId, ':', exceptionsWithRule);
      } else {
        console.error('Erreur lors de la récupération des exceptions:', response.status);
        // Afficher le contenu de la réponse pour debug
        const errorText = await response.text();
        console.error('Contenu de l\'erreur:', errorText);
        setExceptions([]);
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des exceptions:', error);
      setExceptions([]);
    } finally {
      setLoadingExceptions(false);
    }
  };

  useEffect(() => {
    // Forcer le format 24h au niveau du document
    document.documentElement.setAttribute('lang', 'fr-FR');
    
    // Forcer le format 24h pour les inputs time
    const timeInputs = document.querySelectorAll('input[type="time"]');
    timeInputs.forEach(input => {
      input.setAttribute('data-format', '24h');
    });
  }, []);

  // Récupération des données depuis l'API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        console.log('Utilisateur courant:', currentUser?.team?.id);
        
        if (!currentUser?.team?.id) {
          throw new Error('Utilisateur non assigné à une équipe');
        }
        
        let templatesList = [];
        
        // Récupération des templates
        const templatesResponse = await fetch(`/api/teams/${currentUser.team.id}/shift-templates/list`, {
          headers: getAuthHeaders()
        });
        
        if (templatesResponse.ok) {
          const templatesData = await templatesResponse.json();
          // console.log('Données templates reçues:', templatesData);
          
          templatesList = Array.isArray(templatesData) ? templatesData : 
                         Array.isArray(templatesData.results) ? templatesData.results : 
                         Array.isArray(templatesData.templates) ? templatesData.templates : [];
          
          setTemplates(templatesList);
        }

        // Récupération des utilisateurs
        const usersResponse = await fetch('/api/users/', {
          headers: getAuthHeaders()
        });
        
        if (usersResponse.ok) {
          const usersData = await usersResponse.json();
          const usersList = Array.isArray(usersData) ? usersData : 
                           Array.isArray(usersData.users) ? usersData.users : [];
          setUsers(usersList);
        }

        // Récupération des règles pour tous les templates
        let allRules = [];
        
        if (templatesList.length > 0) {
          for (const template of templatesList) {
            try {
              const rulesResponse = await fetch(`/api/shift-templates/${template.id}/rules/list`, {
                headers: getAuthHeaders()
              });
              
              if (rulesResponse.ok) {
                const rulesData = await rulesResponse.json();
                
                // Extraire les règles depuis results (comme pour les templates)
                const rulesList = Array.isArray(rulesData) ? rulesData : 
                                 Array.isArray(rulesData.results) ? rulesData.results : 
                                 Array.isArray(rulesData.rules) ? rulesData.rules : [];
                
                
                if (rulesList.length > 0) {
                  const rulesWithTemplate = rulesList.map(rule => ({
                    ...rule,
                    template_name: template.name,
                    template_id: template.id
                  }));
                  
                  allRules = [...allRules, ...rulesWithTemplate];
                } else {
                  console.log(`Aucune règle trouvée pour le template ${template.name} (ID: ${template.id})`);
                }
              } else {
                console.warn(`Erreur lors de la récupération des règles pour le template ${template.id}:`, rulesResponse.status);
              }
            } catch (err) {
              console.error(`Erreur lors de la récupération des règles pour le template ${template.id}:`, err);
            }
          }
        }
        
        setRules(allRules);
        console.log('Total des règles récupérées:', allRules.length);
        console.log('Règles finales:', allRules);
        
      } catch (err) {
        console.error('Erreur lors de la récupération des données:', err);
        setError(err.message);
        setTemplates([]);
        setRules([]);
      } finally {
        setLoading(false);
      }
    };

    if (currentUser) {
      fetchData();
    } else {
      setLoading(false);
      setError('Utilisateur non connecté');
    }
  }, [currentUser]);

  // Nouvelles fonctions pour les exceptions
  const openAddException = () => {
    setAddingException(true);
    setNewExceptionData({
      date: new Date().toISOString().split('T')[0],
      is_skipped: false,
      override_start_local_time: '',
      override_duration_minutes: 480,
      note: ''
    });
    setSelectedRule(''); // Reset de la règle sélectionnée
  };

  const closeAddException = () => {
    setAddingException(false);
    setSelectedRule(''); // Reset de la règle sélectionnée
  };

  const openEditException = (exception) => {
    setEditingException({ ...exception });
    setSelectedRule(exception.rule_id?.toString() || '');
  };
  
  const closeEditException = () => {
    setEditingException(null);
    setSelectedRule(''); // Reset de la règle sélectionnée
  };

  const handleAddException = async () => {
    if (!selectedRule) {
      showErrorModal('Erreur de validation', 'Veuillez sélectionner une règle');
      return;
    }
    if (!newExceptionData.date) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une date');
      return;
    }
    if (!newExceptionData.is_skipped && !newExceptionData.override_start_local_time) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une heure de début ou cocher "Ignorer"');
      return;
    }
    
    try {
      const payload = {
        ...newExceptionData,
        override_start_local_time: newExceptionData.is_skipped ? null : 
          (newExceptionData.override_start_local_time ? 
            `${newExceptionData.override_start_local_time}:${new Date().toISOString().substr(17)}` : null),
        override_duration_minutes: newExceptionData.is_skipped ? null : 
          parseInt(newExceptionData.override_duration_minutes) || null
      };
      
      console.log('Création exception - Données envoyées:', payload);
      
      const response = await fetch(`/api/shift-rules/${selectedRule}/exceptions`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        const ruleInfo = rules.find(r => r.id === parseInt(selectedRule));
        const newException = {
          ...(responseData.exception || responseData),
          rule_name: ruleInfo?.template_name,
          rule_id: ruleInfo?.id
        };
        
        setExceptions(prev => [...prev, newException]);
        closeAddException();
      } else {
        const errorData = await response.json();
        showErrorModal('Erreur de création', errorData.message || 'Erreur lors de la création de l\'exception');
      }
    } catch (err) {
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur');
    }
  };

  const openViewException = (exception) => setViewingException(exception);
  const closeViewException = () => setViewingException(null);


  const askDeleteException = (exception) => setDeletingException(exception);
  const cancelDeleteException = () => setDeletingException(null);
  
  const confirmDeleteException = async () => {
    try {
      const response = await fetch(`/api/shift-rules/${deletingException.rule_id}/exceptions/${deletingException.id}/`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        setExceptions(prev => prev.filter(e => e.id !== deletingException.id));
        if (viewingException?.id === deletingException.id) setViewingException(null);
        if (editingException?.id === deletingException.id) setEditingException(null);
        setDeletingException(null);
      } else {
        showErrorModal('Erreur de suppression', 'Impossible de supprimer l\'exception');
      }
    } catch (err) {
      showErrorModal('Erreur réseau', 'Impossible de supprimer l\'exception');
    }
  };

  const handleSaveException = async () => {
    if (!editingException.date) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une date');
      return;
    }
    if (!editingException.is_skipped && !editingException.override_start_local_time) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une heure de début ou cocher "Ignorer"');
      return;
    }
    if (!editingException.is_skipped && (!editingException.override_duration_minutes || editingException.override_duration_minutes <= 0)) {
      showErrorModal('Erreur de validation', 'Veuillez saisir une durée valide');
      return;
    }

    try {
      let formattedStartTime = null;
      if (!editingException.is_skipped && editingException.override_start_local_time) {
        if (typeof editingException.override_start_local_time === 'string' && editingException.override_start_local_time.includes(':')) {
          formattedStartTime = `${editingException.override_start_local_time}:${new Date().toISOString().substr(17)}`;
        } else {
          formattedStartTime = editingException.override_start_local_time;
        }
      }

      const payload = {
        date: editingException.date,
        is_skipped: editingException.is_skipped,
        override_start_local_time: formattedStartTime,
        override_duration_minutes: editingException.is_skipped ? null : parseInt(editingException.override_duration_minutes) || null,
        note: editingException.note || ''
      };
      
      console.log('Modification exception - Données envoyées:', payload);
      
      const response = await fetch(`/api/shift-rules/${editingException.rule_id}/exceptions/${editingException.id}/`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        const updatedException = responseData.exception || responseData;

        setExceptions(prev => prev.map(exception => 
          exception.id === editingException.id ? { 
            ...updatedException, 
            rule_name: editingException.rule_name, 
            rule_id: editingException.rule_id 
          } : exception
        ));

        if (viewingException?.id === editingException.id) {
          setViewingException({ 
            ...updatedException, 
            rule_name: editingException.rule_name, 
            rule_id: editingException.rule_id 
          });
        }

        closeEditException();
      } else {
        let errorMessage = 'Erreur lors de la modification de l\'exception';
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch {
          const errorText = await response.text();  
          errorMessage = errorText || errorMessage;
        }
        
        showErrorModal('Erreur de modification', errorMessage);
      }
    } catch (err) {
      console.error('Erreur:', err);
      showErrorModal('Erreur réseau', 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.');
    }
  };

  // Fonction pour formater la date
  const formatDate = (dateString) => {
    if (!dateString) return 'Non défini';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR');
    } catch {
      return 'Format invalide';
    }
  };

  if (loading) {
    return (
      <div className="horaires-page-container">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <p>Chargement des données...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="horaires-page-container">
        <div style={{ textAlign: 'center', padding: '50px', color: 'red' }}>
          <p>Erreur: {error}</p>
          <button onClick={() => window.location.reload()}>
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="horaires-main-container">
      {/* Navigation par onglets MISE À JOUR */}
      <div className="horaires-tabs-container">
        <div className="horaires-tabs">
          <button 
            className={`horaires-tab ${activeTab === 'templates' ? 'active' : ''}`}
            onClick={() => setActiveTab('templates')}
          >
            📋 Templates de Planning
          </button>
          <button 
            className={`horaires-tab ${activeTab === 'rules' ? 'active' : ''}`}
            onClick={() => setActiveTab('rules')}
          >
            📝 Règles de Planning
          </button>
          <button 
            className={`horaires-tab ${activeTab === 'exceptions' ? 'active' : ''}`}
            onClick={() => setActiveTab('exceptions')}
          >
            ⚠️ Exceptions des Règles
          </button>
        </div>
        
        {/* Bouton de génération - toujours visible */}
        <button className="template-generate-button" onClick={generateTemplate}>
          ⚡ Générer un planning
        </button>
      </div>

      {/* SECTION TEMPLATES - Affichée seulement si activeTab === 'templates' */}
      {activeTab === 'templates' && (
        <div className="horaires-page-container">
          <div className="horaires-page-header">
            <h1 className="horaires-page-title">Templates de Planning</h1>
            <p className="horaires-page-description">Gestion des templates de planning pour votre équipe</p>
            <button className="horaires-add-button" onClick={openAddHoraire}>
              + Ajouter un template
            </button>
          </div>

          <div className="horaires-table-container">
            <table className="horaires-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Durée par défaut</th>
                  <th>Fuseau horaire</th>
                  <th>Rôle</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {templates.map((template) => (
                  <tr key={template.id} onClick={() => openView(template)} style={{ cursor: 'pointer' }}>
                    <td>{template.name || 'Nom non défini'}</td>
                    <td>{formatDuration(template.default_duration_minutes)}</td>
                    <td>{template.timezone || 'Non défini'}</td>
                    <td>{template.role_id ? `Rôle ${template.role_id}` : 'Tous les rôles'}</td>
                    <td>{template.is_active ? '✅ Actif' : '❌ Inactif'}</td>
                    <td className="horaires-actions-cell" onClick={(e) => e.stopPropagation()}>
                      <button className="horaires-btn horaires-btn-edit" onClick={() => openEdit(template)}>
                        Modifier
                      </button>
                      <button className="horaires-btn horaires-btn-delete" onClick={() => askDelete(template)}>
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
                {templates.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: 20, color: '#666' }}>
                      Aucun template de planning enregistré
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* SECTION RÈGLES - Affichée seulement si activeTab === 'rules' */}
      {activeTab === 'rules' && (
        <div className="horaires-page-container">
          <div className="horaires-page-header">
            <h1 className="horaires-page-title">Règles de Planning</h1>
            <p className="horaires-page-description">Gestion des règles de planning pour les templates</p>
            <button className="horaires-add-button" onClick={openAddRule}>
              + Ajouter une règle
            </button>
          </div>

          <div className="horaires-table-container">
            <table className="horaires-table">
              <thead>
                <tr>
                  <th>Template</th>
                  <th>Jour</th>
                  <th>Heure de début</th>
                  <th>Durée</th>
                  <th>Période</th>
                  <th>Assignation</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rules.map((rule) => (
                  <tr key={rule.id} onClick={() => openViewRule(rule)} style={{ cursor: 'pointer' }}>
                    <td>{rule.template_name || 'Template non défini'}</td>
                    <td>{getWeekdayName(rule.weekday)}</td>
                    <td>{formatTime(rule.start_local_time)}</td>
                    <td>{formatDuration(rule.duration_minutes)}</td>
                    <td>{rule.effective_from} - {rule.effective_to}</td>
                    <td>{rule.apply_to_whole_team ? 'Toute l\'équipe' : `${rule.assigned_user_ids?.length || 0} utilisateur(s)`}</td>
                    <td className="horaires-actions-cell" onClick={(e) => e.stopPropagation()}>
                      <button className="horaires-btn horaires-btn-edit" onClick={() => openEditRule(rule)}>
                        Modifier
                      </button>
                      <button className="horaires-btn horaires-btn-delete" onClick={() => askDeleteRule(rule)}>
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
                {rules.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: 20, color: '#666' }}>
                      {templates.length === 0 ? 'Créez d\'abord des templates' : 'Aucune règle de planning enregistrée'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* NOUVELLE SECTION EXCEPTIONS - Affichée seulement si activeTab === 'exceptions' */}
      {activeTab === 'exceptions' && (
        <div className="horaires-page-container">
          <div className="horaires-page-header">
            <h1 className="horaires-page-title">Exceptions des Règles</h1>
            <p className="horaires-page-description">Gestion des exceptions pour les règles de planning</p>
            <button className="horaires-add-button" onClick={openAddException}>
              + Ajouter une exception
            </button>
          </div>

          {/* Sélecteur de règle pour filtrer */}
          <div style={{ marginBottom: '20px', textAlign: 'center' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>
              Filtrer par règle :
            </label>
            <select 
              value={selectedRule} 
              onChange={(e) => {
                setSelectedRule(e.target.value);
                fetchExceptions(e.target.value);
              }}
              style={{ 
                padding: '8px 12px', 
                fontSize: '14px', 
                borderRadius: '6px', 
                border: '1px solid #ddd',
                minWidth: '300px'
              }}
            >
              <option value="">— Toutes les règles —</option>
              {rules.map((rule) => (
                <option key={rule.id} value={rule.id}>
                  {rule.template_name} - {getWeekdayName(rule.weekday)} {formatTime(rule.start_local_time)}
                </option>
              ))}
            </select>
          </div>

          <div className="horaires-table-container">
            <table className="horaires-table">
              <thead>
                <tr>
                  <th>Règle</th>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Heure modifiée</th>
                  <th>Durée modifiée</th>
                  <th>Note</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loadingExceptions ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: 20, color: '#666' }}>
                      Chargement des exceptions...
                    </td>
                  </tr>
                ) : exceptions.length > 0 ? (
                  exceptions.map((exception) => (
                    <tr key={exception.id} onClick={() => openViewException(exception)} style={{ cursor: 'pointer' }}>
                      <td>{exception.rule_name || 'Règle inconnue'}</td>
                      <td>{formatDate(exception.date)}</td>
                      <td>{exception.is_skipped ? '🚫 Ignorée' : '📝 Modifiée'}</td>
                      <td>{exception.is_skipped ? '-' : formatTime(exception.override_start_local_time)}</td>
                      <td>{exception.is_skipped ? '-' : formatDuration(exception.override_duration_minutes)}</td>
                      <td>{exception.note || '-'}</td>
                      <td className="horaires-actions-cell" onClick={(e) => e.stopPropagation()}>
                        <button className="horaires-btn horaires-btn-edit" onClick={() => openEditException(exception)}>
                          Modifier
                        </button>
                        <button className="horaires-btn horaires-btn-delete" onClick={() => askDeleteException(exception)}>
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: 20, color: '#666' }}>
                      {selectedRule ? 'Aucune exception pour cette règle' : 'Sélectionnez une règle pour voir les exceptions'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODALES TEMPLATES */}
      {/* Modal pour ajouter un template */}
      {addingHoraire && (
        <div className="horaires-modal-overlay" onClick={closeAddHoraire}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Ajouter un template de planning</h2>
              <button className="horaires-modal-close" onClick={closeAddHoraire}>
                ×
              </button>
            </div>

            <label>Nom du template *</label>
            <input
              type="text"
              value={newHoraireData.name}
              onChange={(e) => setNewHoraireData({...newHoraireData, name: e.target.value})}
              placeholder="Ex: Planning Équipe Jour, Planning Weekend..."
              autoFocus
            />

            <label>Durée par défaut (minutes) *</label>
            <input
              type="number"
              value={newHoraireData.default_duration_minutes}
              onChange={(e) => setNewHoraireData({...newHoraireData, default_duration_minutes: parseInt(e.target.value) || 0})}
              min="1"
              placeholder="Ex: 480 pour 8h"
            />

            <label>Fuseau horaire *</label>
            <select
              value={newHoraireData.timezone}
              onChange={(e) => setNewHoraireData({...newHoraireData, timezone: e.target.value})}
              className="timezone-select"
            >
              <option value="Europe/Paris">Europe/Paris</option>
              <option value="UTC">UTC</option>
              <option value="Europe/London">Europe/London</option>
              <option value="America/New_York">America/New_York</option>
              <option value="Asia/Tokyo">Asia/Tokyo</option>
            </select>

            <label>Rôle spécifique (optionnel)</label>
            <input
              type="number"
              value={newHoraireData.role_id || ''}
              onChange={(e) => setNewHoraireData({...newHoraireData, role_id: e.target.value ? parseInt(e.target.value) : null})}
              placeholder="Laisser vide pour tous les rôles"
              min="1"
            />

            <label>
              <input
                type="checkbox"
                checked={newHoraireData.is_active}
                onChange={(e) => setNewHoraireData({...newHoraireData, is_active: e.target.checked})}
              />
              Template actif
            </label>

            <div className="horaires-modal-buttons" style={{ marginTop: 16 }}>
              <button className="horaires-btn horaires-btn-save" onClick={handleAddHoraire}>
                Créer le template
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeAddHoraire}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de visualisation */}
      {viewingHoraire && (
        <div className="horaires-modal-overlay" onClick={closeView}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Template de planning</h2>
              <button className="horaires-modal-close" onClick={closeView}>
                ×
              </button>
            </div>
            
            <div className="horaires-modal-info">
              <p><strong>Nom :</strong> {viewingHoraire.name || 'Non défini'}</p>
              <p><strong>Durée par défaut :</strong> {formatDuration(viewingHoraire.default_duration_minutes)}</p>
              <p><strong>Fuseau horaire :</strong> {viewingHoraire.timezone || 'Non défini'}</p>
              <p><strong>Rôle :</strong> {viewingHoraire.role_id ? `Rôle ${viewingHoraire.role_id}` : 'Tous les rôles'}</p>
              <p><strong>Statut :</strong> {viewingHoraire.is_active ? 'Actif' : 'Inactif'}</p>
            </div>

            <div className="horaires-modal-buttons" style={{ marginTop: 20 }}>
              <button className="horaires-btn horaires-btn-edit" onClick={() => {
                closeView();
                openEdit(viewingHoraire);
              }}>
                Modifier ce template
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeView}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de suppression */}
      {deletingHoraire && (
        <div className="horaires-modal-overlay" onClick={cancelDelete}>
          <div className="horaires-modal horaires-delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>
              Êtes-vous sûr de vouloir supprimer le template{" "}
              <strong>{deletingHoraire.name}</strong> ?
            </h2>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-delete" onClick={confirmDelete}>
                Supprimer
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={cancelDelete}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal d'erreur */}
      {errorModal.show && (
        <div className="horaires-modal-overlay" onClick={closeErrorModal}>
          <div className="horaires-modal horaires-error-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2 style={{ color: '#dc3545' }}>{errorModal.title}</h2>
              <button className="horaires-modal-close" onClick={closeErrorModal}>
                ×
              </button>
            </div>
            <div className="horaires-modal-body" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px', color: '#dc3545' }}>⚠️</span>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>
                  {errorModal.message}
                </p>
              </div>
            </div>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-cancel" onClick={closeErrorModal}>
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de modification adaptée aux templates */}
      {editingHoraire && (
        <div className="horaires-modal-overlay" onClick={closeEdit}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Modifier le template</h2>
              <button className="horaires-modal-close" onClick={closeEdit}>
                ×
              </button>
            </div>

            <label>Nom du template *</label>
            <input
              type="text"
              value={editingHoraire.name || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, name: e.target.value })}
            />

            <label>Durée par défaut (minutes) *</label>
            <input
              type="number"
              value={editingHoraire.default_duration_minutes || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, default_duration_minutes: parseInt(e.target.value) || 0 })}
              min="1"
            />

            <label>Fuseau horaire *</label>
            <select
              value={editingHoraire.timezone || 'Europe/Paris'}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, timezone: e.target.value })}
              className="timezone-select"
            >
              <option value="Europe/Paris">Europe/Paris</option>
              <option value="UTC">UTC</option>
              <option value="Europe/London">Europe/London</option>
              <option value="America/New_York">America/New_York</option>
              <option value="Asia/Tokyo">Asia/Tokyo</option>
            </select>

            <label>Rôle spécifique (optionnel)</label>
            <input
              type="number"
              value={editingHoraire.role_id || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, role_id: e.target.value ? parseInt(e.target.value) : null })}
              placeholder="Laisser vide pour tous les rôles"
              min="1"
            />

            <label>
              <input
                type="checkbox"
                checked={editingHoraire.is_active || false}
                onChange={(e) => setEditingHoraire({ ...editingHoraire, is_active: e.target.checked })}
              />
              Template actif
            </label>

            <div className="horaires-modal-buttons" style={{ marginTop: 16 }}>
              <button className="horaires-btn horaires-btn-save" onClick={handleSave}>
                Valider
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeEdit}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* NOUVELLES MODALES RÈGLES */}
      {/* Modal pour ajouter une règle */}
      {addingRule && (
        <div className="horaires-modal-overlay" onClick={closeAddRule}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Ajouter une règle de planning</h2>
              <button className="horaires-modal-close" onClick={closeAddRule}>×</button>
            </div>

            <label>Template *</label>
            <select 
              value={selectedTemplate} 
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="template-select"
            >
              <option value="">— Sélectionner un template —</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>{template.name}</option>
              ))}
            </select>

            <label>Jour de la semaine *</label>
            <select 
              value={newRuleData.weekday} 
              onChange={(e) => setNewRuleData({...newRuleData, weekday: parseInt(e.target.value)})}
              className="weekday-select"
            >
              {weekdays.map((day) => (
                <option key={day.id} value={day.id}>{day.name}</option>
              ))}
            </select>

            <label>Heure de début *</label>
            <input
              type="time"
              value={newRuleData.start_local_time}
              onChange={(e) => setNewRuleData({...newRuleData, start_local_time: e.target.value})}
              step="60"
              min="00:00"
              max="23:59"
              pattern="[0-9]{2}:[0-9]{2}"
              title="Format 24h: HH:MM (ex: 14:30)"
              placeholder="HH:MM"
            />

            <label>Durée (minutes) *</label>
            <input
              type="number"
              value={newRuleData.duration_minutes}
              onChange={(e) => setNewRuleData({...newRuleData, duration_minutes: parseInt(e.target.value) || 0})}
              min="1"
            />

            {/* Conteneur amélioré pour les dates */}
            <div className="date-range-container">
              <div className="date-field">
                <label>Date de début *</label>
                <input
                  type="date"
                  value={newRuleData.effective_from}
                  onChange={(e) => setNewRuleData({...newRuleData, effective_from: e.target.value})}
                  min={new Date().toISOString().split('T')[0]} // Pas de dates passées
                />
              </div>
              
              <div className="date-field">
                <label>Date de fin *</label>
                <input
                  type="date"
                  value={newRuleData.effective_to}
                  onChange={(e) => setNewRuleData({...newRuleData, effective_to: e.target.value})}
                  min={newRuleData.effective_from || new Date().toISOString().split('T')[0]} // Min = date de début
                />
              </div>
            </div>

            <label>
              <input
                type="checkbox"
                checked={newRuleData.apply_to_whole_team}
                onChange={(e) => setNewRuleData({...newRuleData, apply_to_whole_team: e.target.checked})}
              />
              Appliquer à toute l'équipe
            </label>

            {!newRuleData.apply_to_whole_team && (
              <div>
                <label>Utilisateurs assignés</label>
                <div className="user-selection-area">
                  {users.map((user) => (
                    <label key={user.id}>
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.id)}
                        onChange={() => handleUserSelection(user.id)}
                      />
                      {user.first_name} {user.last_name} ({user.email})
                    </label>
                  ))}
                </div>
              </div>
            )}

            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-save" onClick={handleAddRule}>
                Créer la règle
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeAddRule}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de visualisation */}
      {viewingRule && (
        <div className="horaires-modal-overlay" onClick={closeViewRule}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Détails de la règle</h2>
              <button className="horaires-modal-close" onClick={closeViewRule}>
                ×
              </button>
            </div>
            
            <div className="horaires-modal-info">
              <p><strong>Template :</strong> {viewingRule.template_name || 'Non défini'}</p>
              <p><strong>Jour de la semaine :</strong> {getWeekdayName(viewingRule.weekday)}</p>
              <p><strong>Heure de début :</strong> {formatTime(viewingRule.start_local_time)}</p>
              <p><strong>Durée :</strong> {formatDuration(viewingRule.duration_minutes)}</p>
              <p><strong>Période :</strong> {viewingRule.effective_from} - {viewingRule.effective_to}</p>
              <p><strong>Assignation :</strong> {viewingRule.apply_to_whole_team ? 'Toute l\'équipe' : `${viewingRule.assigned_user_ids?.length || 0} utilisateur(s)`}</p>
              <p><strong>Statut :</strong> {viewingRule.is_active ? 'Active' : 'Inactive'}</p>
            </div>

            <div className="horaires-modal-buttons" style={{ marginTop: 20 }}>
              <button className="horaires-btn horaires-btn-edit" onClick={() => {
                closeViewRule();
                openEditRule(viewingRule);
              }}>
                Modifier cette règle
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeViewRule}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de suppression */}
      {deletingRule && (
        <div className="horaires-modal-overlay" onClick={cancelDeleteRule}>
          <div className="horaires-modal horaires-delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>
              Êtes-vous sûr de vouloir supprimer cette règle ?
            </h2>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-delete" onClick={confirmDeleteRule}>
                Supprimer
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={cancelDeleteRule}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal d'erreur */}
      {errorModal.show && (
        <div className="horaires-modal-overlay" onClick={closeErrorModal}>
          <div className="horaires-modal horaires-error-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2 style={{ color: '#dc3545' }}>{errorModal.title}</h2>
              <button className="horaires-modal-close" onClick={closeErrorModal}>
                ×
              </button>
            </div>
            <div className="horaires-modal-body" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px', color: '#dc3545' }}>⚠️</span>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>
                  {errorModal.message}
                </p>
              </div>
            </div>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-cancel" onClick={closeErrorModal}>
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de modification adaptée aux templates */}
      {editingHoraire && (
        <div className="horaires-modal-overlay" onClick={closeEdit}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Modifier le template</h2>
              <button className="horaires-modal-close" onClick={closeEdit}>
                ×
              </button>
            </div>

            <label>Nom du template *</label>
            <input
              type="text"
              value={editingHoraire.name || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, name: e.target.value })}
            />

            <label>Durée par défaut (minutes) *</label>
            <input
              type="number"
              value={editingHoraire.default_duration_minutes || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, default_duration_minutes: parseInt(e.target.value) || 0 })}
              min="1"
            />

            <label>Fuseau horaire *</label>
            <select
              value={editingHoraire.timezone || 'Europe/Paris'}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, timezone: e.target.value })}
              className="timezone-select"
            >
              <option value="Europe/Paris">Europe/Paris</option>
              <option value="UTC">UTC</option>
              <option value="Europe/London">Europe/London</option>
              <option value="America/New_York">America/New_York</option>
              <option value="Asia/Tokyo">Asia/Tokyo</option>
            </select>

            <label>Rôle spécifique (optionnel)</label>
            <input
              type="number"
              value={editingHoraire.role_id || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, role_id: e.target.value ? parseInt(e.target.value) : null })}
              placeholder="Laisser vide pour tous les rôles"
              min="1"
            />

            <label>
              <input
                type="checkbox"
                checked={editingHoraire.is_active || false}
                onChange={(e) => setEditingHoraire({ ...editingHoraire, is_active: e.target.checked })}
              />
              Template actif
            </label>

            <div className="horaires-modal-buttons" style={{ marginTop: 16 }}>
              <button className="horaires-btn horaires-btn-save" onClick={handleSave}>
                Valider
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeEdit}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* NOUVELLES MODALES RÈGLES */}
      {/* Modal pour ajouter une règle */}
      {addingRule && (
        <div className="horaires-modal-overlay" onClick={closeAddRule}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Ajouter une règle de planning</h2>
              <button className="horaires-modal-close" onClick={closeAddRule}>×</button>
            </div>

            <label>Template *</label>
            <select 
              value={selectedTemplate} 
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="template-select"
            >
              <option value="">— Sélectionner un template —</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>{template.name}</option>
              ))}
            </select>

            <label>Jour de la semaine *</label>
            <select 
              value={newRuleData.weekday} 
              onChange={(e) => setNewRuleData({...newRuleData, weekday: parseInt(e.target.value)})}
              className="weekday-select"
            >
              {weekdays.map((day) => (
                <option key={day.id} value={day.id}>{day.name}</option>
              ))}
            </select>

            <label>Heure de début *</label>
            <input
              type="time"
              value={newRuleData.start_local_time}
              onChange={(e) => setNewRuleData({...newRuleData, start_local_time: e.target.value})}
              step="60"
              min="00:00"
              max="23:59"
              pattern="[0-9]{2}:[0-9]{2}"
              title="Format 24h: HH:MM (ex: 14:30)"
              placeholder="HH:MM"
            />

            <label>Durée (minutes) *</label>
            <input
              type="number"
              value={newRuleData.duration_minutes}
              onChange={(e) => setNewRuleData({...newRuleData, duration_minutes: parseInt(e.target.value) || 0})}
              min="1"
            />

            {/* Conteneur amélioré pour les dates */}
            <div className="date-range-container">
              <div className="date-field">
                <label>Date de début *</label>
                <input
                  type="date"
                  value={newRuleData.effective_from}
                  onChange={(e) => setNewRuleData({...newRuleData, effective_from: e.target.value})}
                  min={new Date().toISOString().split('T')[0]} // Pas de dates passées
                />
              </div>
              
              <div className="date-field">
                <label>Date de fin *</label>
                <input
                  type="date"
                  value={newRuleData.effective_to}
                  onChange={(e) => setNewRuleData({...newRuleData, effective_to: e.target.value})}
                  min={newRuleData.effective_from || new Date().toISOString().split('T')[0]} // Min = date de début
                />
              </div>
            </div>

            <label>
              <input
                type="checkbox"
                checked={newRuleData.apply_to_whole_team}
                onChange={(e) => setNewRuleData({...newRuleData, apply_to_whole_team: e.target.checked})}
              />
              Appliquer à toute l'équipe
            </label>

            {!newRuleData.apply_to_whole_team && (
              <div>
                <label>Utilisateurs assignés</label>
                <div className="user-selection-area">
                  {users.map((user) => (
                    <label key={user.id}>
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.id)}
                        onChange={() => handleUserSelection(user.id)}
                      />
                      {user.first_name} {user.last_name} ({user.email})
                    </label>
                  ))}
                </div>
              </div>
            )}

            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-save" onClick={handleAddRule}>
                Créer la règle
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeAddRule}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de visualisation */}
      {viewingRule && (
        <div className="horaires-modal-overlay" onClick={closeViewRule}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Détails de la règle</h2>
              <button className="horaires-modal-close" onClick={closeViewRule}>
                ×
              </button>
            </div>
            
            <div className="horaires-modal-info">
              <p><strong>Template :</strong> {viewingRule.template_name || 'Non défini'}</p>
              <p><strong>Jour de la semaine :</strong> {getWeekdayName(viewingRule.weekday)}</p>
              <p><strong>Heure de début :</strong> {formatTime(viewingRule.start_local_time)}</p>
              <p><strong>Durée :</strong> {formatDuration(viewingRule.duration_minutes)}</p>
              <p><strong>Période :</strong> {viewingRule.effective_from} - {viewingRule.effective_to}</p>
              <p><strong>Assignation :</strong> {viewingRule.apply_to_whole_team ? 'Toute l\'équipe' : `${viewingRule.assigned_user_ids?.length || 0} utilisateur(s)`}</p>
              <p><strong>Statut :</strong> {viewingRule.is_active ? 'Active' : 'Inactive'}</p>
            </div>

            <div className="horaires-modal-buttons" style={{ marginTop: 20 }}>
              <button className="horaires-btn horaires-btn-edit" onClick={() => {
                closeViewRule();
                openEditRule(viewingRule);
              }}>
                Modifier cette règle
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeViewRule}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de suppression */}
      {deletingRule && (
        <div className="horaires-modal-overlay" onClick={cancelDeleteRule}>
          <div className="horaires-modal horaires-delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>
              Êtes-vous sûr de vouloir supprimer cette règle ?
            </h2>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-delete" onClick={confirmDeleteRule}>
                Supprimer
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={cancelDeleteRule}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal d'erreur */}
      {errorModal.show && (
        <div className="horaires-modal-overlay" onClick={closeErrorModal}>
          <div className="horaires-modal horaires-error-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2 style={{ color: '#dc3545' }}>{errorModal.title}</h2>
              <button className="horaires-modal-close" onClick={closeErrorModal}>
                ×
              </button>
            </div>
            <div className="horaires-modal-body" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px', color: '#dc3545' }}>⚠️</span>
                <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.5' }}>
                  {errorModal.message}
                </p>
              </div>
            </div>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-cancel" onClick={closeErrorModal}>
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de modification adaptée aux templates */}
      {editingHoraire && (
        <div className="horaires-modal-overlay" onClick={closeEdit}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Modifier le template</h2>
              <button className="horaires-modal-close" onClick={closeEdit}>
                ×
              </button>
            </div>

            <label>Nom du template *</label>
            <input
              type="text"
              value={editingHoraire.name || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, name: e.target.value })}
            />

            <label>Durée par défaut (minutes) *</label>
            <input
              type="number"
              value={editingHoraire.default_duration_minutes || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, default_duration_minutes: parseInt(e.target.value) || 0 })}
              min="1"
            />

            <label>Fuseau horaire *</label>
            <select
              value={editingHoraire.timezone || 'Europe/Paris'}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, timezone: e.target.value })}
              className="timezone-select"
            >
              <option value="Europe/Paris">Europe/Paris</option>
              <option value="UTC">UTC</option>
              <option value="Europe/London">Europe/London</option>
              <option value="America/New_York">America/New_York</option>
              <option value="Asia/Tokyo">Asia/Tokyo</option>
            </select>

            <label>Rôle spécifique (optionnel)</label>
            <input
              type="number"
              value={editingHoraire.role_id || ''}
              onChange={(e) => setEditingHoraire({ ...editingHoraire, role_id: e.target.value ? parseInt(e.target.value) : null })}
              placeholder="Laisser vide pour tous les rôles"
              min="1"
            />

            <label>
              <input
                type="checkbox"
                checked={editingHoraire.is_active || false}
                onChange={(e) => setEditingHoraire({ ...editingHoraire, is_active: e.target.checked })}
              />
              Template actif
            </label>

            <div className="horaires-modal-buttons" style={{ marginTop: 16 }}>
              <button className="horaires-btn horaires-btn-save" onClick={handleSave}>
                Valider
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeEdit}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* NOUVELLES MODALES RÈGLES */}
      {/* Modal pour ajouter une règle */}
      {addingRule && (
        <div className="horaires-modal-overlay" onClick={closeAddRule}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Ajouter une règle de planning</h2>
              <button className="horaires-modal-close" onClick={closeAddRule}>×</button>
            </div>

            <label>Template *</label>
            <select 
              value={selectedTemplate} 
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="template-select"
            >
              <option value="">— Sélectionner un template —</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>{template.name}</option>
              ))}
            </select>

            <label>Jour de la semaine *</label>
            <select 
              value={newRuleData.weekday} 
              onChange={(e) => setNewRuleData({...newRuleData, weekday: parseInt(e.target.value)})}
              className="weekday-select"
            >
              {weekdays.map((day) => (
                <option key={day.id} value={day.id}>{day.name}</option>
              ))}
            </select>

            <label>Heure de début *</label>
            <input
              type="time"
              value={newRuleData.start_local_time}
              onChange={(e) => setNewRuleData({...newRuleData, start_local_time: e.target.value})}
              step="60"
              min="00:00"
              max="23:59"
              pattern="[0-9]{2}:[0-9]{2}"
              title="Format 24h: HH:MM (ex: 14:30)"
              placeholder="HH:MM"
            />

            <label>Durée (minutes) *</label>
            <input
              type="number"
              value={newRuleData.duration_minutes}
              onChange={(e) => setNewRuleData({...newRuleData, duration_minutes: parseInt(e.target.value) || 0})}
              min="1"
            />

            {/* Conteneur amélioré pour les dates */}
            <div className="date-range-container">
              <div className="date-field">
                <label>Date de début *</label>
                <input
                  type="date"
                  value={newRuleData.effective_from}
                  onChange={(e) => setNewRuleData({...newRuleData, effective_from: e.target.value})}
                  min={new Date().toISOString().split('T')[0]} // Pas de dates passées
                />
              </div>
              
              <div className="date-field">
                <label>Date de fin *</label>
                <input
                  type="date"
                  value={newRuleData.effective_to}
                  onChange={(e) => setNewRuleData({...newRuleData, effective_to: e.target.value})}
                  min={newRuleData.effective_from || new Date().toISOString().split('T')[0]} // Min = date de début
                />
              </div>
            </div>

            <label>
              <input
                type="checkbox"
                checked={newRuleData.apply_to_whole_team}
                onChange={(e) => setNewRuleData({...newRuleData, apply_to_whole_team: e.target.checked})}
              />
              Appliquer à toute l'équipe
            </label>

            {!newRuleData.apply_to_whole_team && (
              <div>
                <label>Utilisateurs assignés</label>
                <div className="user-selection-area">
                  {users.map((user) => (
                    <label key={user.id}>
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.id)}
                        onChange={() => handleUserSelection(user.id)}
                      />
                      {user.first_name} {user.last_name} ({user.email})
                    </label>
                  ))}
                </div>
              </div>
            )}

            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-save" onClick={handleAddRule}>
                Créer la règle
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeAddRule}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de visualisation */}
      {viewingRule && (
        <div className="horaires-modal-overlay" onClick={closeViewRule}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Détails de la règle</h2>
              <button className="horaires-modal-close" onClick={closeViewRule}>
                ×
              </button>
            </div>
            
            <div className="horaires-modal-info">
              <p><strong>Template :</strong> {viewingRule.template_name || 'Non défini'}</p>
              <p><strong>Jour de la semaine :</strong> {getWeekdayName(viewingRule.weekday)}</p>
              <p><strong>Heure de début :</strong> {formatTime(viewingRule.start_local_time)}</p>
              <p><strong>Durée :</strong> {formatDuration(viewingRule.duration_minutes)}</p>
              <p><strong>Période :</strong> {viewingRule.effective_from} - {viewingRule.effective_to}</p>
              <p><strong>Assignation :</strong> {viewingRule.apply_to_whole_team ? 'Toute l\'équipe' : `${viewingRule.assigned_user_ids?.length || 0} utilisateur(s)`}</p>
              <p><strong>Statut :</strong> {viewingRule.is_active ? 'Active' : 'Inactive'}</p>
            </div>

            <div className="horaires-modal-buttons" style={{ marginTop: 20 }}>
              <button className="horaires-btn horaires-btn-edit" onClick={() => {
                closeViewRule();
                openEditRule(viewingRule);
              }}>
                Modifier cette règle
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeViewRule}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de suppression */}
      {deletingRule && (
        <div className="horaires-modal-overlay" onClick={cancelDeleteRule}>
          <div className="horaires-modal horaires-delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>
              Êtes-vous sûr de vouloir supprimer cette règle ?
            </h2>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-delete" onClick={confirmDeleteRule}>
                Supprimer
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={cancelDeleteRule}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODALES EXCEPTIONS */}
      {/* Modal pour ajouter une exception */}
      {addingException && (
        <div className="horaires-modal-overlay" onClick={closeAddException}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Ajouter une exception</h2>
              <button className="horaires-modal-close" onClick={closeAddException}>×</button>
            </div>

            <label>Règle *</label>
            <select 
              value={selectedRule} 
              onChange={(e) => setSelectedRule(e.target.value)}
              className="template-select"
            >
              <option value="">— Sélectionner une règle —</option>
              {rules.map((rule) => (
                <option key={rule.id} value={rule.id}>
                  {rule.template_name} - {getWeekdayName(rule.weekday)} {formatTime(rule.start_local_time)}
                </option>
              ))}
            </select>

            <label>Date *</label>
            <input
              type="date"
              value={newExceptionData.date}
              onChange={(e) => setNewExceptionData({...newExceptionData, date: e.target.value})}
              min={new Date().toISOString().split('T')[0]}
            />

            <label>
              <input
                type="checkbox"
                checked={newExceptionData.is_skipped}
                onChange={(e) => setNewExceptionData({...newExceptionData, is_skipped: e.target.checked})}
              />
              Ignorer cette occurrence (pas de shift ce jour-là)
            </label>

            {!newExceptionData.is_skipped && (
              <>
                <label>Heure de début modifiée</label>
                <input
                  type="time"
                  value={newExceptionData.override_start_local_time}
                  onChange={(e) => setNewExceptionData({...newExceptionData, override_start_local_time: e.target.value})}
                  step="60"
                  min="00:00"
                  max="23:59"
                />

                <label>Durée modifiée (minutes)</label>
                <input
                  type="number"
                  value={newExceptionData.override_duration_minutes}
                  onChange={(e) => setNewExceptionData({...newExceptionData, override_duration_minutes: parseInt(e.target.value) || 0})}
                  min="1"
                />
              </>
            )}

            <label>Note (optionnelle)</label>
            <textarea
              value={newExceptionData.note}
              onChange={(e) => setNewExceptionData({...newExceptionData, note: e.target.value})}
              placeholder="Raison de l'exception..."
              rows="3"
            />

            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-save" onClick={handleAddException}>
                Créer l'exception
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeAddException}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de visualisation des exceptions */}
      {viewingException && (
        <div className="horaires-modal-overlay" onClick={closeViewException}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Exception de règle</h2>
              <button className="horaires-modal-close" onClick={closeViewException}>×</button>
            </div>
            
            <div className="horaires-modal-info">
              <p><strong>Règle :</strong> {viewingException.rule_name || 'Non définie'}</p>
              <p><strong>Date :</strong> {formatDate(viewingException.date)}</p>
              <p><strong>Type :</strong> {viewingException.is_skipped ? 'Occurrence ignorée' : 'Horaires modifiés'}</p>
              {!viewingException.is_skipped && (
                <>
                  <p><strong>Heure modifiée :</strong> {formatTime(viewingException.override_start_local_time)}</p>
                  <p><strong>Durée modifiée :</strong> {formatDuration(viewingException.override_duration_minutes)}</p>
                </>
              )}
              <p><strong>Note :</strong> {viewingException.note || 'Aucune note'}</p>
            </div>

            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-edit" onClick={() => {
                closeViewException();
                openEditException(viewingException);
              }}>
                Modifier cette exception
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeViewException}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de modification des exceptions */}
      {editingException && (
        <div className="horaires-modal-overlay" onClick={closeEditException}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Modifier l'exception</h2>
              <button className="horaires-modal-close" onClick={closeEditException}>×</button>
            </div>

            <label>Règle (non modifiable)</label>
            <input
              type="text"
              value={editingException.rule_name || 'Règle inconnue'}
              disabled
              style={{ backgroundColor: '#f8f9fa', color: '#6c757d' }}
            />

            <label>Date *</label>
            <input
              type="date"
              value={editingException.date || ''}
              onChange={(e) => setEditingException({ ...editingException, date: e.target.value })}
            />

            <label>
              <input
                type="checkbox"
                checked={editingException.is_skipped || false}
                onChange={(e) => setEditingException({ ...editingException, is_skipped: e.target.checked })}
              />
              Ignorer cette occurrence (pas de shift ce jour-là)
            </label>

            {!editingException.is_skipped && (
              <>
                <label>Heure de début modifiée</label>
                <input
                  type="time"
                  value={isoToTimeInput(editingException.override_start_local_time)}
                  onChange={(e) => setEditingException({ ...editingException, override_start_local_time: e.target.value })}
                  step="60"
                  min="00:00"
                  max="23:59"
                />

                <label>Durée modifiée (minutes)</label>
                <input
                  type="number"
                  value={editingException.override_duration_minutes || ''}
                  onChange={(e) => setEditingException({ ...editingException, override_duration_minutes: parseInt(e.target.value) || 0 })}
                  min="1"
                />
              </>
            )}

            <label>Note (optionnelle)</label>
            <textarea
              value={editingException.note || ''}
              onChange={(e) => setEditingException({ ...editingException, note: e.target.value })}
              placeholder="Raison de l'exception..."
              rows="3"
            />

            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-save" onClick={handleSaveException}>
                Valider
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeEditException}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de suppression des exceptions */}
      {deletingException && (
        <div className="horaires-modal-overlay" onClick={cancelDeleteException}>
          <div className="horaires-modal horaires-delete-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Êtes-vous sûr de vouloir supprimer cette exception ?</h2>
            <p>Date : <strong>{formatDate(deletingException.date)}</strong></p>
            <div className="horaires-modal-buttons">
              <button className="horaires-btn horaires-btn-delete" onClick={confirmDeleteException}>
                Supprimer
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={cancelDeleteException}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal pour générer un planning */}
      {generatingTemplate && (
        <div className="horaires-modal-overlay" onClick={closeGenerateTemplate}>
          <div className="horaires-modal horaires-form-modal" onClick={(e) => e.stopPropagation()}>
            <div className="horaires-modal-header">
              <h2>Générer un planning</h2>
              <button className="horaires-modal-close" onClick={closeGenerateTemplate}>
                ×
              </button>
            </div>

            <label>Nombre de jours à partir d'aujourd'hui *</label>
            <input
              type="number"
              value={numberOfDays}
              onChange={(e) => setNumberOfDays(parseInt(e.target.value) || 0)}
              min="1"
              max="365"
              placeholder="Ex: 7 pour une semaine"
              style={{ marginBottom: '10px' }}
              autoFocus
            />
            
            {/* Affichage de la période calculée */}
            {numberOfDays > 0 && (
              <div style={{ 
                backgroundColor: '#e9ecef', 
                padding: '15px', 
                borderRadius: '8px', 
                fontSize: '14px',
                color: '#495057',
                marginBottom: '15px',
                textAlign: 'center'
              }}>
                <strong>Période de génération :</strong><br />
                Du {new Date().toLocaleDateString('fr-FR')} au{' '}
                {new Date(Date.now() + (numberOfDays - 1) * 24 * 60 * 60 * 1000).toLocaleDateString('fr-FR')}
                <br />
                <em>({numberOfDays} jour{numberOfDays > 1 ? 's' : ''})</em>
              </div>
            )}

            <div className="horaires-modal-buttons" style={{ marginTop: 20 }}>
              <button 
                className="horaires-btn horaires-btn-save" 
                onClick={handleGenerateTemplate}
                disabled={!numberOfDays || numberOfDays <= 0}
              >
                Générer le planning
              </button>
              <button className="horaires-btn horaires-btn-cancel" onClick={closeGenerateTemplate}>
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Horaires;