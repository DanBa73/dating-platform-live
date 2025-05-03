# accounts/adapter.py
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Wird von allauth aufgerufen, wenn ein Benutzer gespeichert wird
        (z.B. bei der Registrierung).
        Wir rufen zuerst die Standardmethode auf und fügen dann unsere Felder hinzu.
        """
        # Rufe zuerst die Standardmethode auf, um den User mit den Basisdaten zu speichern
        # Wichtig: commit=False verwenden, falls wir die Daten *vor* dem finalen DB-Speichern setzen wollen
        # Aber da gender/seeking null=True erlauben, können wir es auch danach machen.
        # Wir lassen commit=True und speichern einfach nochmal.
        user = super().save_user(request, user, form, commit=commit)

        # Hole gender und seeking aus den validierten Formulardaten
        # Wichtig: form.cleaned_data verwenden!
        user.gender = form.cleaned_data.get('gender')
        user.seeking = form.cleaned_data.get('seeking')

        # Speichere die Änderungen an gender und seeking, falls commit=True war
        # oder falls wir commit=False verwendet hätten, wäre hier das finale user.save()
        if commit:
            user.save(update_fields=['gender', 'seeking'])

        return user