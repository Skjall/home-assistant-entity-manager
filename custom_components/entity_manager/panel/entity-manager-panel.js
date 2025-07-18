import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class EntityManagerPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
      selectedArea: { type: String },
      selectedDomain: { type: String },
      skipMaintained: { type: Boolean },
      areas: { type: Array },
      domains: { type: Array },
      entities: { type: Array },
      selectedEntities: { type: Set },
      loading: { type: Boolean },
      processing: { type: Boolean },
    };
  }

  constructor() {
    super();
    this.selectedArea = "";
    this.selectedDomain = "";
    this.skipMaintained = false;
    this.areas = [];
    this.domains = [];
    this.entities = [];
    this.selectedEntities = new Set();
    this.loading = false;
    this.processing = false;
  }

  static get styles() {
    return css`
      :host {
        display: block;
        height: 100%;
        background-color: var(--primary-background-color);
      }

      .header {
        background-color: var(--app-header-background-color);
        color: var(--app-header-text-color);
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--material-shadow-elevation-2dp);
      }

      .header h1 {
        margin: 0;
        font-size: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .content {
        padding: 16px;
        max-width: 1200px;
        margin: 0 auto;
      }

      .controls {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: var(--material-shadow-elevation-2dp);
      }

      .control-row {
        display: grid;
        grid-template-columns: 1fr 1fr auto;
        gap: 16px;
        align-items: end;
      }

      .control-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      label {
        font-weight: 500;
        color: var(--primary-text-color);
      }

      select, button {
        padding: 8px 12px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        font-size: 14px;
      }

      select {
        cursor: pointer;
      }

      button {
        cursor: pointer;
        background: var(--primary-color);
        color: var(--text-primary-color);
        border: none;
        font-weight: 500;
        transition: background-color 0.2s;
      }

      button:hover:not(:disabled) {
        background: var(--dark-primary-color);
      }

      button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .entities-container {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        box-shadow: var(--material-shadow-elevation-2dp);
      }

      .entities-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--divider-color);
      }

      .entity-card {
        background: var(--card-background-color);
        border: 2px solid var(--divider-color);
        border-radius: 4px;
        padding: 12px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s;
      }

      .entity-card:hover {
        box-shadow: var(--material-shadow-elevation-4dp);
        transform: translateX(4px);
      }

      .entity-card.selected {
        border-color: var(--primary-color);
        background: var(--primary-color-light, rgba(3, 169, 244, 0.1));
      }

      .entity-card.needs-rename {
        background: var(--warning-color-light, rgba(255, 193, 7, 0.1));
      }

      .entity-card.needs-rename.selected {
        background: linear-gradient(to right, 
          var(--primary-color-light, rgba(3, 169, 244, 0.1)) 0%, 
          var(--warning-color-light, rgba(255, 193, 7, 0.1)) 100%);
      }

      .entity-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .entity-ids {
        flex: 1;
      }

      .entity-id {
        font-family: monospace;
        font-size: 14px;
        color: var(--primary-text-color);
      }

      .entity-new-id {
        font-family: monospace;
        font-size: 12px;
        color: var(--secondary-text-color);
        margin-top: 4px;
      }

      .entity-status {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      .tag {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
      }

      .tag.rename {
        background: var(--warning-color);
        color: var(--text-warning-color, white);
      }

      .tag.maintained {
        background: var(--success-color);
        color: var(--text-success-color, white);
      }

      .checkbox-container {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .process-button {
        background: var(--success-color);
        color: white;
        padding: 12px 24px;
        font-size: 16px;
      }

      .loading {
        text-align: center;
        padding: 40px;
        color: var(--secondary-text-color);
      }

      .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--secondary-text-color);
      }

      .empty-state ha-icon {
        --mdi-icon-size: 64px;
        margin-bottom: 16px;
        opacity: 0.3;
      }

      @media (max-width: 768px) {
        .control-row {
          grid-template-columns: 1fr;
        }
      }
    `;
  }

  render() {
    return html`
      <div class="header">
        <h1>
          <ha-icon icon="mdi:rename-box"></ha-icon>
          Entity Manager
        </h1>
        <div>
          ${this.hass?.user?.is_admin
            ? html`<span>Admin Mode</span>`
            : html`<span>Read Only</span>`}
        </div>
      </div>

      <div class="content">
        <div class="controls">
          <div class="control-row">
            <div class="control-group">
              <label>Area</label>
              <select
                .value=${this.selectedArea}
                @change=${this._onAreaChange}
                ?disabled=${this.loading || this.processing}
              >
                <option value="">Select an area...</option>
                ${this.areas.map(
                  (area) => html`
                    <option value=${area.name}>
                      ${area.name} (${area.entity_count} entities)
                    </option>
                  `
                )}
              </select>
            </div>

            <div class="control-group">
              <label>Domain</label>
              <select
                .value=${this.selectedDomain}
                @change=${this._onDomainChange}
                ?disabled=${!this.selectedArea || this.loading || this.processing}
              >
                <option value="">All domains</option>
                ${this.domains.map(
                  (domain) => html`
                    <option value=${domain}>${domain}</option>
                  `
                )}
              </select>
            </div>

            <div class="control-group">
              <div class="checkbox-container">
                <input
                  type="checkbox"
                  id="skip-maintained"
                  .checked=${this.skipMaintained}
                  @change=${this._onSkipMaintainedChange}
                  ?disabled=${this.loading || this.processing}
                />
                <label for="skip-maintained">Skip maintained entities</label>
              </div>
              <button
                @click=${this._loadEntities}
                ?disabled=${!this.selectedArea || this.loading || this.processing}
              >
                ${this.loading ? "Loading..." : "Preview"}
              </button>
            </div>
          </div>
        </div>

        ${this.entities.length > 0
          ? html`
              <div class="entities-container">
                <div class="entities-header">
                  <h2>
                    ${this.selectedEntities.size} of ${this.entities.length} selected
                  </h2>
                  <div>
                    <button @click=${this._selectAll}>Select All</button>
                    <button @click=${this._selectNone}>Select None</button>
                    <button
                      class="process-button"
                      @click=${this._processEntities}
                      ?disabled=${this.selectedEntities.size === 0 || this.processing}
                    >
                      ${this.processing
                        ? "Processing..."
                        : `Process ${this.selectedEntities.size} entities`}
                    </button>
                  </div>
                </div>

                ${this.entities.map(
                  (entity) => html`
                    <div
                      class="entity-card ${entity.needs_rename
                        ? "needs-rename"
                        : ""} ${this.selectedEntities.has(entity.entity_id)
                        ? "selected"
                        : ""}"
                      @click=${() => this._toggleEntity(entity.entity_id)}
                    >
                      <div class="entity-info">
                        <div class="entity-ids">
                          <div class="entity-id">${entity.entity_id}</div>
                          ${entity.needs_rename
                            ? html`
                                <div class="entity-new-id">
                                  → ${entity.new_entity_id}
                                </div>
                              `
                            : ""}
                        </div>
                        <div class="entity-status">
                          ${entity.needs_rename
                            ? html`<span class="tag rename">Needs Rename</span>`
                            : ""}
                          ${entity.has_maintained_label
                            ? html`<span class="tag maintained">Maintained</span>`
                            : ""}
                        </div>
                      </div>
                    </div>
                  `
                )}
              </div>
            `
          : this.loading
          ? html`
              <div class="loading">
                <ha-circular-progress active></ha-circular-progress>
                <p>Loading entities...</p>
              </div>
            `
          : this.selectedArea
          ? html`
              <div class="empty-state">
                <ha-icon icon="mdi:folder-open-outline"></ha-icon>
                <h2>No entities found</h2>
                <p>
                  No entities found in ${this.selectedArea}
                  ${this.selectedDomain ? `with domain ${this.selectedDomain}` : ""}
                </p>
              </div>
            `
          : html`
              <div class="empty-state">
                <ha-icon icon="mdi:home-outline"></ha-icon>
                <h2>Select an area to get started</h2>
                <p>Choose an area from the dropdown above to view and manage entities</p>
              </div>
            `}
      </div>
    `;
  }

  async firstUpdated() {
    await this._loadAreas();
  }

  async _loadAreas() {
    this.loading = true;
    try {
      const response = await this.hass.callWS({
        type: "entity_manager/get_areas",
      });
      this.areas = response.areas.sort((a, b) => a.name.localeCompare(b.name));
    } catch (error) {
      console.error("Failed to load areas:", error);
      this._showError("Failed to load areas");
    } finally {
      this.loading = false;
    }
  }

  async _onAreaChange(e) {
    this.selectedArea = e.target.value;
    this.selectedDomain = "";
    this.entities = [];
    this.selectedEntities.clear();
    
    if (this.selectedArea) {
      // Load available domains for this area
      await this._loadDomains();
    }
  }

  async _loadDomains() {
    // For now, we'll use a predefined list. In a future version,
    // we could dynamically detect available domains
    this.domains = [
      "light",
      "switch",
      "sensor",
      "binary_sensor",
      "climate",
      "cover",
      "fan",
      "lock",
      "media_player",
      "vacuum",
    ];
  }

  _onDomainChange(e) {
    this.selectedDomain = e.target.value;
  }

  _onSkipMaintainedChange(e) {
    this.skipMaintained = e.target.checked;
  }

  async _loadEntities() {
    if (!this.selectedArea) return;

    this.loading = true;
    this.entities = [];
    this.selectedEntities.clear();

    try {
      const response = await this.hass.callWS({
        type: "entity_manager/get_entities_by_area",
        area_name: this.selectedArea,
        domain: this.selectedDomain || undefined,
        skip_maintained: this.skipMaintained,
      });

      this.entities = response.entities;
      
      // Auto-select entities that need renaming
      this.entities.forEach((entity) => {
        if (entity.needs_rename) {
          this.selectedEntities.add(entity.entity_id);
        }
      });
      
      this.requestUpdate();
    } catch (error) {
      console.error("Failed to load entities:", error);
      this._showError("Failed to load entities");
    } finally {
      this.loading = false;
    }
  }

  _toggleEntity(entityId) {
    if (this.selectedEntities.has(entityId)) {
      this.selectedEntities.delete(entityId);
    } else {
      this.selectedEntities.add(entityId);
    }
    this.requestUpdate();
  }

  _selectAll() {
    this.entities.forEach((entity) => {
      this.selectedEntities.add(entity.entity_id);
    });
    this.requestUpdate();
  }

  _selectNone() {
    this.selectedEntities.clear();
    this.requestUpdate();
  }

  async _processEntities() {
    if (this.selectedEntities.size === 0) return;

    const confirmed = await this._confirm(
      `Are you sure you want to rename ${this.selectedEntities.size} entities?`
    );
    if (!confirmed) return;

    this.processing = true;

    try {
      const entityIds = Array.from(this.selectedEntities);
      const response = await this.hass.callWS({
        type: "entity_manager/rename_entities",
        entity_ids: entityIds,
      });

      const successful = response.results.filter((r) => r.success).length;
      const failed = response.results.filter((r) => !r.success).length;

      let message = `Successfully renamed ${successful} entities.`;
      if (failed > 0) {
        message += ` ${failed} entities failed.`;
      }

      this._showSuccess(message);

      // Reload entities to show updated state
      await this._loadEntities();
    } catch (error) {
      console.error("Failed to rename entities:", error);
      this._showError("Failed to rename entities");
    } finally {
      this.processing = false;
    }
  }

  async _confirm(message) {
    return confirm(message);
  }

  _showSuccess(message) {
    this.hass.callService("persistent_notification", "create", {
      title: "Entity Manager",
      message: message,
      notification_id: "entity_manager_success",
    });
  }

  _showError(message) {
    this.hass.callService("persistent_notification", "create", {
      title: "Entity Manager Error",
      message: message,
      notification_id: "entity_manager_error",
    });
  }
}

customElements.define("entity-manager-panel", EntityManagerPanel);